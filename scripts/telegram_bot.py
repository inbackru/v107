#!/usr/bin/env python3
"""
InBack Telegram Bot — 2026 edition
────────────────────────────────────────────────────────────────────────────────
UX principles:
  • All navigation edits the same message in place (no message flood)
  • Back button always works — nav stack stored in user_data
  • Multi-step conversation flows (application, linking) use FSM states
  • Manager panel is a separate branch detected by telegram_id lookup
  • Owner (TELEGRAM_CHAT_ID) gets all system notifications
  • Manager registration: 6-digit code generated on the website

Manager onboarding (how to connect):
  1. Manager opens their profile on inback.ru → "Получить код для Telegram"
  2. A 6-digit code is shown (valid 10 min)
  3. Manager opens @Inback_bot → /link XXXXXX
  4. Bot links their account and shows Manager Panel
────────────────────────────────────────────────────────────────────────────────
"""

import os
import logging
import requests
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from app import app, db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── env ───────────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set!")

OWNER_CHAT_ID      = os.environ.get('TELEGRAM_CHAT_ID', '')
SITE_URL           = os.environ.get('SITE_URL', 'https://inback.ru')
# Internal URL for Flask API calls — uses localhost so it works in both dev and prod
INTERNAL_URL       = os.environ.get('INTERNAL_URL', 'http://127.0.0.1:5000')
BOT_WEBHOOK_SECRET = os.environ.get('BOT_WEBHOOK_SECRET', 'inback_bot_secret_2024')

# In-memory store: telegram_id → last chat room_id used by that manager
# Lets manager reply with plain text after first #ID reply (no need to repeat #ID each time)
_mgr_last_room: dict = {}

# Maps tg_id → {telegram_msg_id: room_id} — enables native Reply routing for site-chat
_tg_room_msg_map: dict = {}


def send_chat_notify(manager_tg_id: str, room_id: int, sender_name: str, text: str) -> bool:
    """Send new-message notification to manager and store reply mapping.
    Manager can then reply natively (Telegram Reply) to route answer to the chat room.
    """
    if not TELEGRAM_BOT_TOKEN:
        return False
    try:
        tg_text = (
            f"💬 <b>Новое сообщение в чате InBack</b>\n\n"
            f"👤 <b>От:</b> {sender_name}\n"
            f"🏠 Комната #{room_id}\n\n"
            f"✉️ {text[:500]}\n\n"
            f"<i>💡 Нажмите «Ответить» на это сообщение или напишите:</i>\n"
            f"<code>#{room_id} Ваш ответ</code>"
        )
        url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': manager_tg_id,
            'text': tg_text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            msg_id = result.get('result', {}).get('message_id')
            if msg_id:
                if manager_tg_id not in _tg_room_msg_map:
                    _tg_room_msg_map[manager_tg_id] = {}
                # Keep only last 50 messages per manager to avoid unbounded growth
                mapping = _tg_room_msg_map[manager_tg_id]
                if len(mapping) > 50:
                    oldest = sorted(mapping.keys())[0]
                    del mapping[oldest]
                mapping[msg_id] = room_id
                # Also update last room so plain-text works immediately
                _mgr_last_room[manager_tg_id] = room_id
            return True
        return False
    except Exception as e:
        logger.error(f"send_chat_notify: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  DB HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _get_manager_by_tg(tg_id: str):
    from models import Manager
    return Manager.query.filter_by(telegram_id=str(tg_id)).first()


def _get_online_managers():
    from models import Manager
    return Manager.query.filter(
        Manager.is_online == True,
        Manager.telegram_id.isnot(None),
        Manager.telegram_id != ''
    ).order_by(Manager.last_seen_at.desc()).all()


def _get_or_create_support_session(user_tg_id: str, user_name: str, username: str):
    from models import TelegramSupportSession
    s = TelegramSupportSession.query.filter(
        TelegramSupportSession.user_tg_id == user_tg_id,
        TelegramSupportSession.status.in_(['queue', 'active'])
    ).first()
    if not s:
        s = TelegramSupportSession(
            user_tg_id=user_tg_id,
            user_name=user_name,
            user_username=username,
            status='queue'
        )
        db.session.add(s)
        db.session.commit()
    return s


def _store_support_msg(session_id, direction, text,
                       forwarded_msg_id=None, manager_tg_id=None):
    from models import TelegramSupportMessage
    db.session.add(TelegramSupportMessage(
        session_id=session_id,
        direction=direction,
        text=text,
        forwarded_msg_id=forwarded_msg_id,
        manager_tg_id=manager_tg_id,
    ))
    db.session.commit()


def _find_session_by_reply(manager_tg_id: str, reply_msg_id: int):
    from models import TelegramSupportMessage
    m = TelegramSupportMessage.query.filter_by(
        manager_tg_id=manager_tg_id,
        forwarded_msg_id=reply_msg_id,
        direction='user_to_mgr'
    ).first()
    return m.session if m else None


# ── Sync HTTP helper (called from app.py outside async) ──────────────────────

def send_telegram_message(chat_id, text, parse_mode='HTML'):
    if not TELEGRAM_BOT_TOKEN:
        return False
    try:
        url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {'chat_id': chat_id, 'text': text,
                'parse_mode': parse_mode, 'disable_web_page_preview': True}
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            return True
        if 'parse' in resp.text.lower():
            data.pop('parse_mode')
            return requests.post(url, data=data, timeout=10).status_code == 200
        logger.error(f"TG {resp.status_code}: {resp.text[:200]}")
        return False
    except Exception as e:
        logger.error(f"send_telegram_message: {e}")
        return False


async def _notify_owner(bot, text: str):
    if OWNER_CHAT_ID:
        try:
            await bot.send_message(chat_id=OWNER_CHAT_ID, text=text,
                                   parse_mode='HTML', disable_web_page_preview=True)
        except Exception as e:
            logger.warning(f"Owner notify failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  SCREEN BUILDERS  — all return (text, InlineKeyboardMarkup)
# ══════════════════════════════════════════════════════════════════════════════

def _back(target='main'):
    return InlineKeyboardButton("◀️ Назад", callback_data=f"screen:{target}")


def _build_main(first_name=''):
    text = (
        f"👋 <b>Привет{', ' + first_name if first_name else ''}!</b>\n\n"
        "🏠 <b>InBack</b> — кэшбек до <b>500 000 ₽</b> при покупке новостройки.\n\n"
        "✅ Бесплатное сопровождение сделки\n"
        "👤 Персональный менеджер 24/7\n"
        "💰 От 3% до 5% стоимости квартиры\n\n"
        "Выберите раздел:"
    )
    kb = [
        [
            InlineKeyboardButton("💰 Как работает", callback_data="screen:cashback"),
            InlineKeyboardButton("❓ FAQ",           callback_data="screen:faq"),
        ],
        [InlineKeyboardButton("📝 Подать заявку",   callback_data="apply:start")],
        [InlineKeyboardButton("💬 Написать менеджеру", callback_data="screen:chat")],
        [
            InlineKeyboardButton("👤 Мой профиль",  callback_data="screen:profile"),
            InlineKeyboardButton("🌐 Сайт",         url=SITE_URL),
        ],
        [InlineKeyboardButton("ℹ️ Возможности бота", callback_data="screen:help_user")],
    ]
    return text, InlineKeyboardMarkup(kb)


def _build_help_user():
    text = (
        "ℹ️ <b>Возможности бота для покупателей</b>\n\n"

        "📌 <b>Главное меню</b> — /start\n"
        "Вернуться в главное меню в любой момент.\n\n"

        "💰 <b>Как работает кэшбек</b>\n"
        "Узнайте о программе: размер, условия, сроки выплаты.\n\n"

        "❓ <b>FAQ — частые вопросы</b>\n"
        "Ответы на самые популярные вопросы о покупке с кэшбеком.\n\n"

        "📝 <b>Подать заявку</b>\n"
        "Заполните короткую анкету — менеджер свяжется с вами и подберёт объекты.\n\n"

        "💬 <b>Написать менеджеру</b>\n"
        "Живой чат с менеджером прямо в Telegram. Среднее время ответа — 5 минут.\n\n"

        "👤 <b>Мой профиль</b>\n"
        "Просмотр привязанного аккаунта и ссылка в личный кабинет на сайте.\n\n"

        "🌐 <b>Сайт InBack</b>\n"
        f"Каталог новостроек, сравнение, избранное: {SITE_URL}\n\n"

        "━━━━━━━━━━━━━━\n"
        "📋 <b>Доступные команды:</b>\n"
        "/start — главное меню\n"
        "/help — эта справка"
    )
    kb = [[_back()]]
    return text, InlineKeyboardMarkup(kb)


def _build_cashback():
    text = (
        "💰 <b>Кэшбек до 500 000 ₽</b>\n\n"
        "От <b>3% до 5%</b> от стоимости квартиры — прямо на ваш счёт.\n\n"
        "📋 <b>Как получить:</b>\n"
        "  1️⃣ Оставьте заявку через бот или сайт\n"
        "  2️⃣ Менеджер подберёт варианты\n"
        "  3️⃣ Покупаете с нашей помощью\n"
        "  4️⃣ Кэшбек — в течение 30 дней\n\n"
        "🏆 <b>Наши преимущества:</b>\n"
        "  • Без скрытых комиссий\n"
        "  • Все застройщики Краснодарского края\n"
        "  • Юридическая поддержка включена"
    )
    kb = [
        [InlineKeyboardButton("📝 Подать заявку",  callback_data="apply:start")],
        [InlineKeyboardButton("💬 Задать вопрос",  callback_data="screen:chat")],
        [_back()],
    ]
    return text, InlineKeyboardMarkup(kb)


def _build_faq():
    text = (
        "❓ <b>Частые вопросы</b>\n\n"
        "🔹 <b>Сколько составит кэшбек?</b>\n"
        "От 3% до 5% от стоимости (до 500 000 ₽)\n\n"
        "🔹 <b>Когда выплачивается?</b>\n"
        "В течение 30 дней после регистрации в Росреестре\n\n"
        "🔹 <b>Нужно ли платить за услуги?</b>\n"
        "Нет — абсолютно бесплатно для покупателя\n\n"
        "🔹 <b>Какие застройщики?</b>\n"
        "Все ведущие застройщики Краснодарского края\n\n"
        "🔹 <b>Уже есть менеджер в ЖК?</b>\n"
        "Свяжитесь с нами — разберём индивидуально"
    )
    kb = [
        [InlineKeyboardButton("💬 Задать вопрос", callback_data="screen:chat")],
        [InlineKeyboardButton("📝 Подать заявку", callback_data="apply:start")],
        [_back()],
    ]
    return text, InlineKeyboardMarkup(kb)


def _build_profile(tg_id: str):
    from models import User
    user = User.query.filter_by(telegram_id=str(tg_id)).first()
    if user:
        text = (
            f"👤 <b>Ваш профиль</b>\n\n"
            f"Имя: {user.full_name or '—'}\n"
            f"Телефон: {user.phone or '—'}\n"
            f"Email: {user.email or '—'}\n\n"
            f"🔗 <a href='{SITE_URL}/dashboard'>Личный кабинет</a>"
        )
        kb = [[_back()]]
    else:
        text = (
            "👤 <b>Профиль не привязан</b>\n\n"
            "Войдите на сайт через Telegram или укажите свой Telegram ID "
            "в настройках личного кабинета — тогда профиль появится здесь."
        )
        kb = [
            [InlineKeyboardButton("🔗 Войти на сайт", url=f"{SITE_URL}/login")],
            [_back()],
        ]
    return text, InlineKeyboardMarkup(kb)


def _build_chat(user_tg_id: str):
    from models import TelegramSupportSession
    active = TelegramSupportSession.query.filter(
        TelegramSupportSession.user_tg_id == user_tg_id,
        TelegramSupportSession.status.in_(['queue', 'active'])
    ).first()
    online = len(_get_online_managers())

    if active:
        icon   = "🟢" if active.status == 'active' else "⏳"
        status = "Менеджер подключён" if active.status == 'active' else "Ожидаете в очереди"
        text   = (
            f"💬 <b>Чат с поддержкой</b>\n\n"
            f"{icon} {status}\n\n"
            "Пишите сообщения — менеджер видит их.\n"
            "Кнопка ниже завершает сессию."
        )
        kb = [
            [InlineKeyboardButton("❌ Завершить чат", callback_data="chat:end")],
            [_back()],
        ]
    else:
        avail = f"🟢 Онлайн: {online} менедж." if online else "🔴 Все менеджеры заняты"
        text  = (
            f"💬 <b>Написать менеджеру</b>\n\n"
            f"{avail}\n\n"
            "Нажмите «Начать чат» и напишите вопрос.\n"
            "Среднее время ответа: <b>5 минут</b>"
        )
        kb = [
            [InlineKeyboardButton("✉️ Начать чат", callback_data="chat:start")],
            [InlineKeyboardButton("📞 +7 (862) 266-62-16", url="https://t.me/+78622666216")],
            [_back()],
        ]
    return text, InlineKeyboardMarkup(kb)


# ── Manager panel screens ─────────────────────────────────────────────────────

def _build_mgr_main(mgr):
    from models import TelegramSupportSession
    icon_s   = "🟢" if mgr.is_online else "🔴"
    toggle   = ("🔴 Уйти офлайн", "mgr:offline") if mgr.is_online else ("🟢 Выйти онлайн", "mgr:online")
    q_count  = TelegramSupportSession.query.filter_by(status='queue').count()
    a_count  = TelegramSupportSession.query.filter_by(
        manager_tg_id=str(mgr.telegram_id), status='active'
    ).count()
    text = (
        f"🧑‍💼 <b>Панель менеджера</b>\n\n"
        f"Привет, <b>{mgr.first_name or mgr.email}</b>!\n\n"
        f"{icon_s} Статус: <b>{'Онлайн' if mgr.is_online else 'Офлайн'}</b>\n"
        f"💬 Активных чатов: <b>{a_count}</b>\n"
        f"⏳ В очереди: <b>{q_count}</b>"
    )
    kb = [
        [InlineKeyboardButton(toggle[0], callback_data=toggle[1])],
        [
            InlineKeyboardButton("📋 Очередь",    callback_data="mgr:queue"),
            InlineKeyboardButton("📊 Статистика", callback_data="mgr:stats"),
        ],
        [InlineKeyboardButton("🌐 Открыть CRM",  url=f"{SITE_URL}/manager/dashboard")],
        [InlineKeyboardButton("ℹ️ Команды менеджера", callback_data="screen:help_mgr")],
    ]
    return text, InlineKeyboardMarkup(kb)


def _build_help_mgr():
    text = (
        "ℹ️ <b>Возможности бота для менеджеров</b>\n\n"

        "🟢🔴 <b>Статус онлайн / офлайн</b>\n"
        "Управляйте доступностью для входящих чатов прямо из панели.\n\n"

        "📋 <b>Очередь чатов</b>\n"
        "Просматривайте ожидающие обращения и принимайте их одним нажатием.\n\n"

        "📊 <b>Статистика</b>\n"
        "Количество обработанных чатов и закрытых сделок по вашему аккаунту.\n\n"

        "💬 <b>Переписка с клиентами</b>\n"
        "Принятый чат переходит в диалог — пишите клиенту напрямую в Telegram. "
        "Ответы клиента также приходят вам сообщениями.\n\n"

        "🌐 <b>Открыть CRM</b>\n"
        f"Быстрый переход в менеджерский дашборд: {SITE_URL}/manager/dashboard\n\n"

        "━━━━━━━━━━━━━━\n"
        "📋 <b>Доступные команды:</b>\n"
        "/start — главная панель менеджера\n"
        "/online — перейти в статус «Онлайн»\n"
        "/offline — перейти в статус «Офлайн»\n"
        "/stop — отписаться от уведомлений бота\n"
        "/close_N — завершить чат #N (напр. /close_42)\n"
        "/link XXXXXX — привязать Telegram к аккаунту менеджера\n"
        "/help — эта справка\n\n"

        "💡 <b>Как привязать аккаунт:</b>\n"
        "1. Откройте профиль менеджера на сайте\n"
        "2. Нажмите «Получить код для Telegram»\n"
        "3. Отправьте боту: /link КОД"
    )
    kb = [[_back('mgr_main')]]
    return text, InlineKeyboardMarkup(kb)


def _build_mgr_queue(mgr_tg_id: str):
    from models import TelegramSupportSession
    sessions = TelegramSupportSession.query.filter_by(status='queue').all()
    if not sessions:
        return "📋 <b>Очередь пуста</b>\n\nВсе запросы обработаны.", \
               InlineKeyboardMarkup([[_back('mgr_main')]])

    lines = [f"📋 <b>Очередь ({len(sessions)})</b>\n"]
    for s in sessions[:10]:
        uname  = f"@{s.user_username}" if s.user_username else "б/никнейма"
        waited = int((datetime.utcnow() - s.created_at).total_seconds() // 60)
        lines.append(f"• <b>{s.user_name}</b> ({uname}) — {waited} мин")

    buttons = []
    for s in sessions[:5]:
        buttons.append([InlineKeyboardButton(
            f"✅ Принять #{s.id} — {s.user_name}",
            callback_data=f"accept_session:{s.id}"
        )])
    buttons.append([_back('mgr_main')])
    return "\n".join(lines), InlineKeyboardMarkup(buttons)


def _build_mgr_stats(mgr):
    from models import TelegramSupportSession
    total  = TelegramSupportSession.query.filter_by(manager_tg_id=str(mgr.telegram_id)).count()
    closed = TelegramSupportSession.query.filter_by(
        manager_tg_id=str(mgr.telegram_id), status='closed'
    ).count()
    try:
        from models import Deal
        deals = Deal.query.filter_by(manager_id=mgr.id).count()
    except Exception:
        deals = 0
    text = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"💬 Чатов обработано: <b>{total}</b>\n"
        f"✅ Завершено: <b>{closed}</b>\n"
        f"🤝 Сделок в CRM: <b>{deals}</b>\n\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y')}"
    )
    return text, InlineKeyboardMarkup([[_back('mgr_main')]])


# ══════════════════════════════════════════════════════════════════════════════
#  NAVIGATION CORE  — edits the same message every time
# ══════════════════════════════════════════════════════════════════════════════

async def _go(query, screen: str, context: ContextTypes.DEFAULT_TYPE):
    """Navigate to a named screen, always editing the current message."""
    tg_id = str(query.from_user.id)

    # Maintain back-stack
    stack   = context.user_data.setdefault('stack', [])
    current = context.user_data.get('screen')
    if current and current != screen:
        stack.append(current)
        if len(stack) > 8:
            stack.pop(0)
    context.user_data['screen'] = screen

    with app.app_context():
        mgr = _get_manager_by_tg(tg_id)

        if screen == 'mgr_main':
            if not mgr:
                await query.edit_message_text("⛔ Доступ только для менеджеров.")
                return
            text, markup = _build_mgr_main(mgr)
        elif screen == 'mgr_queue':
            if not mgr:
                return
            text, markup = _build_mgr_queue(tg_id)
        elif screen == 'mgr_stats':
            if not mgr:
                return
            text, markup = _build_mgr_stats(mgr)
        elif screen == 'cashback':
            text, markup = _build_cashback()
        elif screen == 'faq':
            text, markup = _build_faq()
        elif screen == 'profile':
            text, markup = _build_profile(tg_id)
        elif screen == 'chat':
            text, markup = _build_chat(tg_id)
        elif screen == 'help_user':
            text, markup = _build_help_user()
        elif screen == 'help_mgr':
            text, markup = _build_help_mgr()
        else:
            # main — reset stack
            context.user_data['stack'] = []
            if mgr:
                text, markup = _build_mgr_main(mgr)
            else:
                text, markup = _build_main(query.from_user.first_name)

    try:
        await query.edit_message_text(text, reply_markup=markup,
                                      parse_mode='HTML', disable_web_page_preview=True)
    except Exception as e:
        if 'not modified' not in str(e).lower():
            logger.warning(f"edit_message_text ({screen}): {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  /start
# ══════════════════════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = str(update.effective_user.id)
    context.user_data['screen'] = 'main'
    context.user_data['stack']  = []

    with app.app_context():
        mgr = _get_manager_by_tg(tg_id)
        if mgr:
            text, markup = _build_mgr_main(mgr)
        else:
            text, markup = _build_main(update.effective_user.first_name)

    await update.message.reply_text(text, reply_markup=markup,
                                    parse_mode='HTML', disable_web_page_preview=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show role-specific help screen as a new message."""
    tg_id = str(update.effective_user.id)
    with app.app_context():
        mgr = _get_manager_by_tg(tg_id)
        if mgr:
            text, markup = _build_help_mgr()
        else:
            text, markup = _build_help_user()
    await update.message.reply_text(text, reply_markup=markup,
                                    parse_mode='HTML', disable_web_page_preview=True)


# ══════════════════════════════════════════════════════════════════════════════
#  INLINE BUTTON ROUTER
# ══════════════════════════════════════════════════════════════════════════════

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data or ''
    tg_id = str(query.from_user.id)

    # ── screen navigation ──────────────────────────────────────────────────
    if data.startswith('screen:'):
        await _go(query, data.split(':', 1)[1], context)
        return

    # ── back (pop stack) ───────────────────────────────────────────────────
    if data == 'back':
        stack = context.user_data.get('stack', [])
        prev  = stack.pop() if stack else 'main'
        context.user_data['stack'] = stack
        await _go(query, prev, context)
        return

    # ── apply flow: start ──────────────────────────────────────────────────
    if data == 'apply:start':
        context.user_data['apply']  = {}
        context.user_data['screen'] = 'apply_name'
        kb = [[InlineKeyboardButton("◀️ Отмена", callback_data="screen:main")]]
        await query.edit_message_text(
            "📝 <b>Заявка</b>  <i>Шаг 1 / 4</i>\n\nКак вас зовут? Введите имя:",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML'
        )
        return

    # ── apply flow: interest (inline buttons) ─────────────────────────────
    if data.startswith('apply:interest:'):
        interest = data.split(':', 2)[2]
        context.user_data.setdefault('apply', {})['interest'] = interest
        await _apply_ask_budget(query, context)
        return

    if data == 'apply:skip_interest':
        context.user_data.setdefault('apply', {})['interest'] = 'Не указано'
        await _apply_ask_budget(query, context)
        return

    # ── apply flow: budget (inline buttons) ───────────────────────────────
    if data.startswith('apply:budget:'):
        budget = data.split(':', 2)[2]
        context.user_data.setdefault('apply', {})['budget'] = budget
        await _apply_show_confirm(query, context)
        return

    if data == 'apply:confirm':
        await _apply_submit(query, context)
        return

    if data == 'apply:cancel':
        context.user_data.pop('apply', None)
        await _go(query, 'main', context)
        return

    # ── chat flow ──────────────────────────────────────────────────────────
    if data == 'chat:start':
        user   = query.from_user
        u_name = user.full_name or user.first_name or 'Клиент'
        uname  = user.username or ''

        with app.app_context():
            session = _get_or_create_support_session(tg_id, u_name, uname)
            sess_id = session.id
            mgrs    = _get_online_managers()
            if mgrs:
                await _broadcast_new_session(query.get_bot(), session, mgrs)

        if mgrs:
            msg = ("💬 <b>Чат начат!</b>\n\n"
                   "Менеджер уже видит обращение — подключится через несколько секунд.\n"
                   "Пишите вопрос прямо сейчас!")
        else:
            msg = ("⏳ <b>Вы в очереди</b>\n\n"
                   "Все менеджеры сейчас заняты — ответят как только освободятся.\n"
                   "Напишите вопрос заранее, мы его увидим.")

        kb = [[InlineKeyboardButton("❌ Завершить чат", callback_data="chat:end")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

        await _notify_owner(
            query.get_bot(),
            f"💬 <b>Новый запрос в поддержку #{sess_id}</b>\n"
            f"👤 {u_name} (@{uname or 'нет'}) • TG: {tg_id}"
        )
        return

    if data == 'chat:end':
        with app.app_context():
            from models import TelegramSupportSession
            sess = TelegramSupportSession.query.filter(
                TelegramSupportSession.user_tg_id == tg_id,
                TelegramSupportSession.status.in_(['queue', 'active'])
            ).first()
            mgr_tg = sess.manager_tg_id if sess else None
            s_id   = sess.id if sess else None
            if sess:
                sess.status    = 'closed'
                sess.closed_at = datetime.utcnow()
                db.session.commit()

        kb = [
            [InlineKeyboardButton("⭐ Оставить отзыв", url=f"{SITE_URL}/reviews")],
            [InlineKeyboardButton("🏠 Главное меню",   callback_data="screen:main")],
        ]
        await query.edit_message_text(
            "✅ <b>Чат завершён</b>\n\nСпасибо за обращение! Если появятся вопросы — мы здесь.",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML'
        )
        if mgr_tg and s_id:
            try:
                await query.get_bot().send_message(
                    chat_id=mgr_tg, text=f"ℹ️ Клиент завершил чат #{s_id}."
                )
            except Exception:
                pass
        return

    # ── manager: online / offline ──────────────────────────────────────────
    if data in ('mgr:online', 'mgr:offline'):
        online_flag = (data == 'mgr:online')
        with app.app_context():
            from models import Manager
            mgr = Manager.query.filter_by(telegram_id=tg_id).first()
            if not mgr:
                await query.answer("Аккаунт не привязан.", show_alert=True)
                return
            mgr.is_online    = online_flag
            mgr.last_seen_at = datetime.utcnow()
            db.session.commit()
            # Re-fetch so screen builder sees fresh data
            mgr_fresh = Manager.query.get(mgr.id)
            text, markup = _build_mgr_main(mgr_fresh)
            mgr_name = mgr_fresh.first_name or mgr_fresh.email

        await query.edit_message_text(text, reply_markup=markup,
                                      parse_mode='HTML', disable_web_page_preview=True)
        status_word = "🟢 вышел онлайн" if online_flag else "🔴 ушёл офлайн"
        await _notify_owner(query.get_bot(),
                            f"👤 Менеджер <b>{mgr_name}</b> {status_word}")

        if online_flag:
            # Show queued sessions to manager who just came online
            with app.app_context():
                from models import TelegramSupportSession
                queued = TelegramSupportSession.query.filter_by(status='queue').limit(5).all()
            for sess in queued:
                uname = f"@{sess.user_username}" if sess.user_username else "б/никнейма"
                kb = [[
                    InlineKeyboardButton("✅ Принять",   callback_data=f"accept_session:{sess.id}"),
                    InlineKeyboardButton("⏩ Пропустить", callback_data=f"skip_session:{sess.id}"),
                ]]
                try:
                    await context.bot.send_message(
                        chat_id=tg_id,
                        text=(f"⏳ <b>В очереди #{sess.id}</b>\n"
                              f"👤 {sess.user_name} ({uname})\n"
                              f"⏱ Ждёт с {sess.created_at.strftime('%H:%M')}"),
                        reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML'
                    )
                except Exception:
                    pass
        return

    if data == 'mgr:queue':
        await _go(query, 'mgr_queue', context)
        return

    if data == 'mgr:stats':
        await _go(query, 'mgr_stats', context)
        return

    # ── accept / skip session ──────────────────────────────────────────────
    if data.startswith('accept_session:'):
        await _accept_session(query, context, int(data.split(':')[1]))
        return

    if data.startswith('skip_session:'):
        await query.edit_message_text("⏩ Пропустили. Другой менеджер примет чат.")
        return

    if data.startswith('close_session_btn:'):
        sess_id = int(data.split(':')[1])
        await _close_session_inline(query, context, sess_id)
        return

    # ── legacy callback aliases (backward compat with old messages) ────────
    _legacy_map = {
        'faq':           'screen:faq',
        'cashback_info': 'screen:cashback',
        'cashback':      'screen:cashback',
        'chat':          'screen:chat',
        'profile':       'screen:profile',
        'main':          'screen:main',
        'write_manager': 'screen:chat',
        'contact':       'screen:chat',
    }
    if data in _legacy_map:
        await _go(query, _legacy_map[data].split(':', 1)[1], context)
        return

    logger.warning(f"Unknown callback: {data}")


# ══════════════════════════════════════════════════════════════════════════════
#  APPLY FLOW  helpers
# ══════════════════════════════════════════════════════════════════════════════

async def _apply_ask_budget(query, context):
    context.user_data['screen'] = 'apply_budget'
    kb = [
        [
            InlineKeyboardButton("до 5 млн",  callback_data="apply:budget:до 5 млн"),
            InlineKeyboardButton("5–10 млн",  callback_data="apply:budget:5–10 млн"),
        ],
        [
            InlineKeyboardButton("10–20 млн", callback_data="apply:budget:10–20 млн"),
            InlineKeyboardButton("от 20 млн", callback_data="apply:budget:от 20 млн"),
        ],
        [InlineKeyboardButton("◀️ Отмена",   callback_data="apply:cancel")],
    ]
    await query.edit_message_text(
        "📝 <b>Заявка</b>  <i>Шаг 3 / 4</i>\n\nКакой у вас бюджет?",
        reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML'
    )


async def _apply_show_confirm(query, context):
    apply = context.user_data.get('apply', {})
    context.user_data['screen'] = 'apply_confirm'
    text = (
        "📝 <b>Заявка</b>  <i>Шаг 4 / 4 — подтверждение</i>\n\n"
        f"👤 Имя: <b>{apply.get('name','—')}</b>\n"
        f"📞 Телефон: <b>{apply.get('phone','—')}</b>\n"
        f"🏠 Интерес: <b>{apply.get('interest','—')}</b>\n"
        f"💰 Бюджет: <b>{apply.get('budget','—')}</b>\n\n"
        "Всё верно?"
    )
    kb = [
        [
            InlineKeyboardButton("✅ Отправить",  callback_data="apply:confirm"),
            InlineKeyboardButton("❌ Отмена",     callback_data="apply:cancel"),
        ]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')


async def _apply_submit(query, context):
    apply = context.user_data.get('apply', {})
    tg_id = str(query.from_user.id)

    with app.app_context():
        lead_id = None
        try:
            from models import Lead
            lead = Lead(
                name=apply.get('name', ''),
                phone=apply.get('phone', ''),
                telegram_id=tg_id,
                source='telegram_bot',
                comment=f"Интерес: {apply.get('interest','—')}\nБюджет: {apply.get('budget','—')}",
                status='new'
            )
            db.session.add(lead)
            db.session.commit()
            lead_id = lead.id
        except Exception as e:
            logger.warning(f"Lead save skipped: {e}")

    kb = [
        [InlineKeyboardButton("💬 Написать менеджеру", callback_data="screen:chat")],
        [InlineKeyboardButton("🏠 Главное меню",       callback_data="screen:main")],
    ]
    await query.edit_message_text(
        f"✅ <b>Заявка #{lead_id or '—'} принята!</b>\n\n"
        f"👤 {apply.get('name','—')} • 📞 {apply.get('phone','—')}\n\n"
        "Менеджер свяжется в течение 15 минут.",
        reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML'
    )
    context.user_data.pop('apply', None)
    context.user_data['screen'] = 'main'

    await _notify_owner(
        query.get_bot(),
        f"📥 <b>Новая заявка из бота!</b>\n"
        f"👤 {apply.get('name','—')} • {apply.get('phone','—')}\n"
        f"🏠 {apply.get('interest','—')} • {apply.get('budget','—')}\n"
        f"🆔 TG: {tg_id}{f' • Лид #{lead_id}' if lead_id else ''}"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

async def _broadcast_new_session(bot, session, managers):
    uname = f"@{session.user_username}" if session.user_username else "без username"
    text  = (
        f"🔔 <b>Новый запрос #{session.id}</b>\n\n"
        f"👤 <b>{session.user_name}</b> ({uname})\n"
        f"🆔 TG: <code>{session.user_tg_id}</code>\n"
        f"🕐 {datetime.utcnow().strftime('%H:%M UTC')}"
    )
    kb = [[
        InlineKeyboardButton("✅ Принять",   callback_data=f"accept_session:{session.id}"),
        InlineKeyboardButton("⏩ Пропустить", callback_data=f"skip_session:{session.id}"),
    ]]
    for mgr in managers:
        try:
            await bot.send_message(
                chat_id=mgr.telegram_id, text=text,
                reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Broadcast to {mgr.telegram_id}: {e}")


async def _accept_session(query, context, session_id: int):
    mgr_tg = str(query.from_user.id)
    with app.app_context():
        from models import TelegramSupportSession, Manager
        sess = TelegramSupportSession.query.get(session_id)
        if not sess:
            await query.edit_message_text("❌ Сессия не найдена.")
            return
        if sess.status == 'active':
            await query.edit_message_text("⚠️ Чат уже принят другим менеджером.")
            return
        if sess.status == 'closed':
            await query.edit_message_text("ℹ️ Чат уже завершён.")
            return

        mgr = Manager.query.filter_by(telegram_id=mgr_tg).first()
        sess.status        = 'active'
        sess.manager_tg_id = mgr_tg
        if mgr:
            sess.manager_db_id = mgr.id
        db.session.commit()

        mgr_name  = (mgr.first_name or mgr.email) if mgr else "Менеджер"
        user_tg   = sess.user_tg_id
        user_name = sess.user_name
        s_id      = sess.id

    kb_mgr = [[
        InlineKeyboardButton(f"🔴 Закрыть чат #{s_id}",
                             callback_data=f"close_session_btn:{s_id}")
    ]]
    await query.edit_message_text(
        f"✅ <b>Чат #{s_id} принят!</b>\n\n"
        f"👤 Клиент: <b>{user_name}</b>\n"
        f"🆔 TG: <code>{user_tg}</code>\n\n"
        "Отвечайте через <b>Reply</b> (удерживайте сообщение → Ответить).\n"
        f"Или используйте: <code>/close_{s_id}</code>",
        reply_markup=InlineKeyboardMarkup(kb_mgr), parse_mode='HTML'
    )
    try:
        await context.bot.send_message(
            chat_id=user_tg,
            text=(f"✅ <b>Менеджер подключился!</b>\n\n"
                  f"👋 Меня зовут <b>{mgr_name}</b>. Слушаю ваш вопрос!\n\n"
                  "<i>Завершить чат: /stop</i>"),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Client notify: {e}")

    await _notify_owner(
        context.bot,
        f"🤝 <b>{mgr_name}</b> принял чат #{s_id} (клиент: {user_name})"
    )


async def _close_session_inline(query, context, sess_id: int):
    mgr_tg = str(query.from_user.id)
    with app.app_context():
        from models import TelegramSupportSession
        sess = TelegramSupportSession.query.get(sess_id)
        if not sess or sess.manager_tg_id != mgr_tg:
            await query.answer("Сессия не найдена.", show_alert=True)
            return
        user_tg    = sess.user_tg_id
        sess.status    = 'closed'
        sess.closed_at = datetime.utcnow()
        db.session.commit()

    await query.edit_message_text(f"✅ Чат #{sess_id} закрыт.")
    try:
        await context.bot.send_message(
            chat_id=user_tg,
            text="✅ Менеджер завершил сессию. Если появятся вопросы — /start"
        )
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  TEXT MESSAGE HANDLER
# ══════════════════════════════════════════════════════════════════════════════

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw     = (update.message.text or '').strip()
    user    = update.effective_user
    tg_id   = str(user.id)
    u_name  = user.full_name or user.first_name or 'Клиент'
    username = user.username or ''

    screen = context.user_data.get('screen', '')

    # ── Apply FSM: name step ───────────────────────────────────────────────
    if screen == 'apply_name':
        context.user_data.setdefault('apply', {})['name'] = raw
        context.user_data['screen'] = 'apply_phone'
        kb = [[InlineKeyboardButton("◀️ Отмена", callback_data="apply:cancel")]]
        await update.message.reply_text(
            f"📝 <b>Заявка</b>  <i>Шаг 2 / 4</i>\n\n"
            f"Отлично, {raw.split()[0]}! 👋\n\nВведите номер телефона:",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML'
        )
        return

    # ── Apply FSM: phone step ─────────────────────────────────────────────
    if screen == 'apply_phone':
        context.user_data.setdefault('apply', {})['phone'] = raw
        context.user_data['screen'] = 'apply_interest'
        kb = [
            [
                InlineKeyboardButton("🛏 Студия",     callback_data="apply:interest:Студия"),
                InlineKeyboardButton("🛏 1–2 комн",   callback_data="apply:interest:1–2 комнаты"),
            ],
            [
                InlineKeyboardButton("🛏 3+ комн",    callback_data="apply:interest:3+ комнаты"),
                InlineKeyboardButton("🏢 Любое",      callback_data="apply:interest:Любое"),
            ],
            [InlineKeyboardButton("⏩ Пропустить",   callback_data="apply:skip_interest")],
        ]
        await update.message.reply_text(
            "📝 <b>Заявка</b>  <i>Шаг 3 / 4</i>\n\nКакой тип квартиры вас интересует?",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML'
        )
        return

    # ── Manager: native Reply → forward to client ─────────────────────────
    with app.app_context():
        mgr = _get_manager_by_tg(tg_id)

    if mgr and update.message.reply_to_message:
        reply_msg_id = update.message.reply_to_message.message_id

        # ── Check if this is a reply to a site-chat notification ──────────────
        room_from_map = _tg_room_msg_map.get(tg_id, {}).get(reply_msg_id)

        # Fallback: extract room_id from the original notification text
        # (survives bot restarts — text always contains "Комната #<id>")
        if not room_from_map:
            import re as _re
            orig_text = (update.message.reply_to_message.text or
                         update.message.reply_to_message.caption or '')
            _m = _re.search(r'Комната\s*#(\d+)', orig_text)
            if _m:
                room_from_map = int(_m.group(1))
                # Restore mapping in memory so subsequent plain-text replies work
                _tg_room_msg_map.setdefault(tg_id, {})[reply_msg_id] = room_from_map
                _mgr_last_room[tg_id] = room_from_map

        if room_from_map:
            try:
                requests.post(
                    f"{INTERNAL_URL}/api/chat/room/{room_from_map}/typing",
                    headers={'X-Bot-Secret': BOT_WEBHOOK_SECRET}, timeout=3
                )
            except Exception:
                pass

            # ── File/Photo reply ──────────────────────────────────────────────
            tg_file = None
            orig_filename = 'file'
            if update.message.photo:
                tg_file = await update.message.photo[-1].get_file()
                orig_filename = f"photo_{tg_file.file_unique_id}.jpg"
            elif update.message.document:
                tg_file = await update.message.document.get_file()
                orig_filename = update.message.document.file_name or f"doc_{tg_file.file_unique_id}"

            if tg_file:
                try:
                    import io
                    bio = io.BytesIO()
                    await tg_file.download_to_memory(bio)
                    bio.seek(0)
                    caption_text = (update.message.caption or '').strip() or None
                    resp = requests.post(
                        f"{INTERNAL_URL}/api/telegram/chat-file-reply",
                        data={'room_id': room_from_map, 'telegram_id': tg_id,
                              'caption': caption_text or ''},
                        files={'file': (orig_filename, bio, 'application/octet-stream')},
                        headers={'X-Bot-Secret': BOT_WEBHOOK_SECRET}, timeout=30
                    )
                    if resp.status_code == 200:
                        _mgr_last_room[tg_id] = room_from_map
                        await update.message.reply_text(
                            f"✅ Файл доставлен в комнату #{room_from_map}.",
                            quote=True
                        )
                    else:
                        await update.message.reply_text(f"⚠️ Ошибка загрузки файла {resp.status_code}", quote=True)
                except Exception as e:
                    await update.message.reply_text(f"❌ Ошибка отправки файла: {e}", quote=True)
                return

            # ── Text reply ────────────────────────────────────────────────────
            try:
                resp = requests.post(
                    f"{INTERNAL_URL}/api/telegram/chat-reply",
                    json={'room_id': room_from_map, 'text': raw, 'telegram_id': tg_id},
                    headers={'X-Bot-Secret': BOT_WEBHOOK_SECRET}, timeout=10
                )
                if resp.status_code == 200:
                    _mgr_last_room[tg_id] = room_from_map
                    await update.message.reply_text(
                        f"✅ Ответ доставлен в комнату #{room_from_map}.\n"
                        f"💡 Теперь можете просто писать — ответы идут в эту же комнату.",
                        quote=True, parse_mode='HTML'
                    )
                else:
                    await update.message.reply_text(f"⚠️ Ошибка {resp.status_code}", quote=True)
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка: {e}", quote=True)
            return

        with app.app_context():
            sess = _find_session_by_reply(tg_id, reply_msg_id)
        if sess:
            with app.app_context():
                from models import TelegramSupportSession
                s = TelegramSupportSession.query.get(sess.id)
                user_tg = s.user_tg_id if s else None
            if user_tg:
                try:
                    await context.bot.send_message(
                        chat_id=user_tg,
                        text=f"💬 <b>Менеджер:</b>\n\n{raw}",
                        parse_mode='HTML'
                    )
                    with app.app_context():
                        _store_support_msg(sess.id, 'mgr_to_user', raw, manager_tg_id=tg_id)
                    await update.message.reply_text("✅ Ответ доставлен.", quote=True)
                except Exception as e:
                    await update.message.reply_text(f"❌ Ошибка: {e}")
            return

    # ── Manager: site-chat reply  #ROOM_ID text ───────────────────────────
    if mgr and raw.startswith('#'):
        import re
        m = re.match(r'^#(\d+)\s+([\s\S]+)', raw)
        if m:
            room_id, reply_text = int(m.group(1)), m.group(2).strip()
            try:
                # Signal typing before sending (shows "печатает..." to client)
                try:
                    requests.post(
                        f"{INTERNAL_URL}/api/chat/room/{room_id}/typing",
                        headers={'X-Bot-Secret': BOT_WEBHOOK_SECRET}, timeout=3
                    )
                except Exception:
                    pass
                resp = requests.post(
                    f"{INTERNAL_URL}/api/telegram/chat-reply",
                    json={'room_id': room_id, 'text': reply_text, 'telegram_id': tg_id},
                    headers={'X-Bot-Secret': BOT_WEBHOOK_SECRET}, timeout=10
                )
                if resp.status_code == 200:
                    _mgr_last_room[tg_id] = room_id
                    # Update manager's last_seen_at so the website shows them as online
                    with app.app_context():
                        try:
                            from models import Manager
                            _m = Manager.query.filter_by(telegram_id=tg_id).first()
                            if _m:
                                _m.last_seen_at = datetime.utcnow()
                                _m.is_online = True
                                db.session.commit()
                        except Exception:
                            pass
                    await update.message.reply_text(
                        f"✅ Доставлено в комнату #{room_id}.\n\n"
                        f"💡 Теперь можете просто писать текст — он уйдёт в эту же комнату.\n"
                        f"Для другой комнаты: <code>#ID текст</code>",
                        parse_mode='HTML'
                    )
                else:
                    await update.message.reply_text(f"⚠️ Ошибка {resp.status_code}")
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка: {e}")
            return

    # ── Manager: plain text → reply to last active room ───────────────────
    if mgr and tg_id in _mgr_last_room:
        import re
        room_id = _mgr_last_room[tg_id]
        # Skip commands and menu items
        if not raw.startswith('/') and len(raw) > 1:
            try:
                resp = requests.post(
                    f"{INTERNAL_URL}/api/telegram/chat-reply",
                    json={'room_id': room_id, 'text': raw, 'telegram_id': tg_id},
                    headers={'X-Bot-Secret': BOT_WEBHOOK_SECRET}, timeout=10
                )
                if resp.status_code == 200:
                    # Update manager's last_seen_at so the website shows them as online
                    with app.app_context():
                        try:
                            from models import Manager
                            _m = Manager.query.filter_by(telegram_id=tg_id).first()
                            if _m:
                                _m.last_seen_at = datetime.utcnow()
                                _m.is_online = True
                                db.session.commit()
                        except Exception:
                            pass
                    await update.message.reply_text(f"✅ → Комната #{room_id}", parse_mode='HTML')
                elif resp.status_code == 404:
                    del _mgr_last_room[tg_id]
                    await update.message.reply_text("⚠️ Комната закрыта или не найдена. Укажите <code>#ID текст</code>", parse_mode='HTML')
                else:
                    await update.message.reply_text(f"⚠️ Ошибка {resp.status_code}")
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка: {e}")
            return

    # ── User in active support session → forward to manager ───────────────
    with app.app_context():
        from models import TelegramSupportSession
        sess = TelegramSupportSession.query.filter(
            TelegramSupportSession.user_tg_id == tg_id,
            TelegramSupportSession.status.in_(['queue', 'active'])
        ).first()

    if sess:
        with app.app_context():
            from models import TelegramSupportSession as TSS
            s = TSS.query.get(sess.id)
            if s and s.status == 'active' and s.manager_tg_id:
                udisp = f"@{username}" if username else "б/никнейма"
                try:
                    sent = await context.bot.send_message(
                        chat_id=s.manager_tg_id,
                        text=f"💬 <b>{u_name}</b> ({udisp}):\n\n{raw}",
                        parse_mode='HTML'
                    )
                    _store_support_msg(s.id, 'user_to_mgr', raw,
                                       forwarded_msg_id=sent.message_id,
                                       manager_tg_id=s.manager_tg_id)
                    s.last_msg_at = datetime.utcnow()
                    db.session.commit()
                    await update.message.reply_text("✅ Отправлено менеджеру.", quote=True)
                except Exception:
                    await update.message.reply_text(
                        "⚠️ Временная ошибка. Попробуйте позже.", quote=True
                    )
            elif s and s.status == 'queue':
                await update.message.reply_text(
                    "⏳ Вы в очереди. Ваш вопрос будет виден менеджеру.", quote=True
                )
        return

    # ── Smart keyword fallback → show main menu ───────────────────────────
    t = raw.lower()
    if any(w in t for w in ['кэшбек', 'кешбек', 'cashback', 'возврат']):
        text, markup = _build_cashback()
    elif any(w in t for w in ['привет', 'здравствуй', 'hello', 'hi', 'добр']):
        text, markup = _build_main(user.first_name)
    elif any(w in t for w in ['телефон', 'контакт', 'позвон', 'номер', 'звон']):
        text  = "📞 <b>Контакты InBack</b>\n\n☎️ 8 (862) 266-62-16\n📧 info@inback.ru\n🌐 inback.ru"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Меню", callback_data="screen:main")]])
    else:
        text, markup = _build_main(user.first_name)

    await update.message.reply_text(text, reply_markup=markup,
                                    parse_mode='HTML', disable_web_page_preview=True)


# ══════════════════════════════════════════════════════════════════════════════
#  COMMANDS
# ══════════════════════════════════════════════════════════════════════════════

async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /link CODE  — link manager account via 6-digit code from the website.
    /link EMAIL — link user account by email (legacy).
    """
    args  = context.args
    tg_id = str(update.effective_user.id)

    if not args:
        await update.message.reply_text(
            "📎 <b>Привязка аккаунта</b>\n\n"
            "<b>Для менеджеров:</b>\n"
            "  1. Откройте профиль на inback.ru\n"
            "  2. Нажмите «Получить код для Telegram»\n"
            "  3. Отправьте: <code>/link КОД</code>\n\n"
            "<b>Для клиентов:</b>\n"
            "  Отправьте: <code>/link ваш@email.ru</code>",
            parse_mode='HTML'
        )
        return

    arg = args[0].strip()

    # ── 6-digit code → manager ─────────────────────────────────────────────
    if arg.isdigit() and len(arg) == 6:
        with app.app_context():
            from models import Manager
            mgr = Manager.query.filter_by(tg_link_code=arg).first()
            if not mgr:
                await update.message.reply_text(
                    "❌ Код не найден.\n"
                    "Сгенерируйте новый в профиле на сайте."
                )
                return
            if mgr.tg_link_code_expires and mgr.tg_link_code_expires < datetime.utcnow():
                await update.message.reply_text(
                    "⏰ Код устарел. Получите новый в профиле."
                )
                return
            mgr.telegram_id           = tg_id
            mgr.tg_link_code          = None
            mgr.tg_link_code_expires  = None
            db.session.commit()
            mgr_name = mgr.first_name or mgr.email
            text_panel, markup_panel = _build_mgr_main(mgr)

        await update.message.reply_text(
            f"✅ <b>Telegram привязан к аккаунту менеджера!</b>\n\n"
            f"Привет, <b>{mgr_name}</b>! 🎉\n\n"
            "Теперь вы будете получать сюда:\n"
            "  🔔 Новые лиды\n"
            "  🤝 Уведомления о сделках\n"
            "  💬 Запросы в поддержку\n\n"
            "Открываю панель менеджера:",
            parse_mode='HTML'
        )
        await update.message.reply_text(text_panel, reply_markup=markup_panel, parse_mode='HTML')
        await _notify_owner(
            context.bot,
            f"🔗 Менеджер <b>{mgr_name}</b> привязал Telegram (id={tg_id})"
        )
        return

    # ── email → user ───────────────────────────────────────────────────────
    if '@' in arg:
        with app.app_context():
            from models import User
            u = User.query.filter_by(email=arg.lower()).first()
            if not u:
                await update.message.reply_text("❌ Пользователь с таким email не найден.")
                return
            u.telegram_id = tg_id
            db.session.commit()
        await update.message.reply_text(
            "✅ Аккаунт привязан! Будете получать уведомления здесь."
        )
        return

    await update.message.reply_text("❌ Формат: <code>/link 123456</code> или <code>/link email@example.ru</code>",
                                    parse_mode='HTML')


async def online_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/online — manager goes online"""
    tg_id = str(update.effective_chat.id)
    with app.app_context():
        from models import Manager
        mgr = Manager.query.filter_by(telegram_id=tg_id).first()
        if not mgr:
            await update.message.reply_text(
                "❌ Аккаунт не привязан.\n\n"
                "Получите код на сайте (профиль → «Получить код для Telegram»),\n"
                "затем: <code>/link КОД</code>",
                parse_mode='HTML'
            )
            return
        mgr.is_online    = True
        mgr.last_seen_at = datetime.utcnow()
        db.session.commit()
        text, markup = _build_mgr_main(mgr)
        mgr_name = mgr.first_name or mgr.email

    await update.message.reply_text(text, reply_markup=markup, parse_mode='HTML')
    await _notify_owner(context.bot, f"🟢 Менеджер <b>{mgr_name}</b> вышел онлайн")


async def offline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/offline — manager goes offline"""
    tg_id = str(update.effective_chat.id)
    with app.app_context():
        from models import Manager
        mgr = Manager.query.filter_by(telegram_id=tg_id).first()
        if not mgr:
            await update.message.reply_text("❌ Аккаунт не привязан.")
            return
        mgr.is_online = False
        db.session.commit()
        text, markup = _build_mgr_main(mgr)
        mgr_name = mgr.first_name or mgr.email

    await update.message.reply_text(text, reply_markup=markup, parse_mode='HTML')
    await _notify_owner(context.bot, f"🔴 Менеджер <b>{mgr_name}</b> ушёл офлайн")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/stop — user ends active support session"""
    tg_id = str(update.effective_chat.id)
    with app.app_context():
        from models import TelegramSupportSession
        sess = TelegramSupportSession.query.filter(
            TelegramSupportSession.user_tg_id == tg_id,
            TelegramSupportSession.status.in_(['queue', 'active'])
        ).first()
        mgr_tg = sess.manager_tg_id if sess else None
        s_id   = sess.id if sess else None
        if sess:
            sess.status    = 'closed'
            sess.closed_at = datetime.utcnow()
            db.session.commit()

    text, markup = _build_main(update.effective_user.first_name)
    await update.message.reply_text("✅ Чат завершён. Спасибо за обращение!")
    await update.message.reply_text(text, reply_markup=markup, parse_mode='HTML')

    if mgr_tg and s_id:
        try:
            await context.bot.send_message(chat_id=mgr_tg, text=f"ℹ️ Клиент завершил чат #{s_id}.")
        except Exception:
            pass


async def close_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/close_N — manager closes session N"""
    import re
    m = re.match(r'^/close_(\d+)', update.message.text or '')
    if not m:
        return
    sess_id = int(m.group(1))
    mgr_tg  = str(update.effective_user.id)

    with app.app_context():
        from models import TelegramSupportSession
        sess = TelegramSupportSession.query.get(sess_id)
        if not sess or sess.manager_tg_id != mgr_tg:
            await update.message.reply_text("❌ Сессия не найдена или не ваша.")
            return
        user_tg    = sess.user_tg_id
        sess.status    = 'closed'
        sess.closed_at = datetime.utcnow()
        db.session.commit()

    await update.message.reply_text(f"✅ Чат #{sess_id} закрыт.")
    try:
        await context.bot.send_message(
            chat_id=user_tg,
            text="✅ Менеджер завершил чат. Если появятся вопросы — /start"
        )
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  NOTIFICATION UTILITIES  (called from app.py via send_telegram_message)
# ══════════════════════════════════════════════════════════════════════════════

def notify_owner_new_lead(lead_name, lead_phone, source='сайт'):
    msg = (
        f"📥 <b>Новый лид!</b>\n\n"
        f"👤 {lead_name}\n📞 {lead_phone}\n📌 {source}\n"
        f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    return send_telegram_message(OWNER_CHAT_ID, msg) if OWNER_CHAT_ID else False


def notify_owner_new_deal(deal_title, client_name, manager_name=''):
    msg = (
        f"🤝 <b>Новая сделка!</b>\n\n"
        f"📋 {deal_title}\n👤 {client_name}\n👔 {manager_name or '—'}\n"
        f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    return send_telegram_message(OWNER_CHAT_ID, msg) if OWNER_CHAT_ID else False


def send_recommendation_notification(user_telegram_id, recommendation_data):
    if not user_telegram_id:
        return False
    msg = (
        f"🏠 <b>Рекомендация от менеджера</b>\n\n"
        f"📋 {recommendation_data.get('title','')}\n"
        f"🏢 {recommendation_data.get('item_name','')}\n"
        f"📝 {recommendation_data.get('description','')}\n\n"
        f"🔗 <a href='{SITE_URL}/{recommendation_data.get('recommendation_type','property')}/"
        f"{recommendation_data.get('item_id','')}'>Посмотреть</a>"
    )
    return send_telegram_message(user_telegram_id, msg)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
        return

    bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    bot_app.add_handler(CommandHandler("start",   start))
    bot_app.add_handler(CommandHandler("help",    help_command))
    bot_app.add_handler(CommandHandler("link",    link_command))
    bot_app.add_handler(CommandHandler("online",  online_command))
    bot_app.add_handler(CommandHandler("offline", offline_command))
    bot_app.add_handler(CommandHandler("stop",    stop_command))

    # /close_N (dynamic pattern)
    bot_app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^/close_\d+'),
        close_session_command
    ))

    # Inline buttons
    bot_app.add_handler(CallbackQueryHandler(button_handler))

    # All text
    bot_app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_message
    ))

    # Register commands with BotFather (visible in the / menu in Telegram)
    async def _set_commands(application):
        from telegram import BotCommand, BotCommandScopeDefault, BotCommandScopeAllPrivateChats
        user_cmds = [
            BotCommand("start",   "Главное меню"),
            BotCommand("help",    "Возможности бота и команды"),
        ]
        mgr_cmds = [
            BotCommand("start",   "Панель менеджера"),
            BotCommand("help",    "Команды и возможности"),
            BotCommand("online",  "Перейти в статус Онлайн"),
            BotCommand("offline", "Перейти в статус Офлайн"),
            BotCommand("stop",    "Отписаться от уведомлений"),
            BotCommand("link",    "Привязать аккаунт: /link КОД"),
        ]
        try:
            await application.bot.set_my_commands(user_cmds, scope=BotCommandScopeDefault())
            logger.info("✅ BotFather commands set (default scope)")
        except Exception as e:
            logger.warning(f"Could not set bot commands: {e}")

    bot_app.post_init = _set_commands

    logger.info("🤖 InBack Bot 2026 — started!")
    logger.info(f"   Owner channel: {OWNER_CHAT_ID or 'NOT SET'}")
    logger.info(f"   Site: {SITE_URL}")
    logger.info("   Manager linking: website profile → 6-digit code → /link CODE")

    bot_app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
