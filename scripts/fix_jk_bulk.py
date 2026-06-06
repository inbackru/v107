"""
fix_jk_bulk.py — массовое обогащение ЖК данными с CIAN.
Берёт все ЖК у которых нет фото / координат / адреса / застройщика
и скрапит их CIAN-страницы.

Запуск:
    python scripts/fix_jk_bulk.py [--city 1] [--limit 50] [--id 370,454]
    python scripts/fix_jk_bulk.py --force   # перезаписать даже имеющиеся данные
"""
import sys, os, re, json, time, html as html_lib, argparse
from datetime import datetime

import psycopg2
import requests
import urllib3
urllib3.disable_warnings()

sys.path.insert(0, os.path.dirname(__file__))

from enrich_complexes import (
    _safe_decode, _strip_html, _parse_about_description,
    _parse_logo_url, _parse_finishing_variants,
)
from parse_jk_by_url import get_or_create_developer, slug_from_name


# ─── Настройки ───────────────────────────────────────────────────────────────
_DIR       = os.path.dirname(__file__)
SETTINGS   = json.load(open(os.path.join(_DIR, '.enrich_settings.json'))) \
             if os.path.exists(os.path.join(_DIR, '.enrich_settings.json')) else {}
PROXY_URL       = SETTINGS.get('proxy_url', '')
REQ_DELAY       = float(SETTINGS.get('delay_between_requests', 2.0))
SESSION_TTL     = 240  # пересоздавать сессию каждые 4 мин (новый IP ротации)
ANTICAPTCHA_KEY = (os.environ.get('ENRICH_ANTICAPTCHA', '').strip()
                   or SETTINGS.get('anticaptcha_key', '').strip())

# Конфиг городов
_CITY_CONFIG: dict = {}
try:
    with open(os.path.join(_DIR, 'city_config.json'), encoding='utf-8') as _cf:
        _CITY_CONFIG = json.load(_cf)
except Exception:
    pass


def _load_jk_cache(city_id: int) -> dict:
    """Загружает кэш Phase 1 для нужного города (per-city + fallback к общему)."""
    for fname in (f'.enrich_cache_city{city_id}.json', '.enrich_cache.json'):
        path = os.path.join(_DIR, fname)
        if os.path.exists(path):
            try:
                return json.load(open(path)).get('jk_search_data', {})
            except Exception:
                pass
    return {}


# Кэш загружается в main() после парсинга --city; пока пустой
_JK_CACHE: dict = {}

_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
}

_sess: requests.Session | None = None
_session_created_at = 0.0

if ANTICAPTCHA_KEY:
    print(f'🔐 Anti-Captcha: ключ установлен ({ANTICAPTCHA_KEY[:6]}...)')


def _solve_anticaptcha(page_url: str, sitekey: str = None) -> str | None:
    """Решает reCAPTCHA v2 через anti-captcha.com. Возвращает token или None."""
    if not ANTICAPTCHA_KEY:
        return None
    try:
        import urllib.request as _urlreq
        _sitekey = sitekey or '6LdO5_IbAAAAAAeVBL9TClS19XUn-dkjV36k6Foj'
        _api = 'https://api.anti-captcha.com'

        body = json.dumps({
            'clientKey': ANTICAPTCHA_KEY,
            'task': {
                'type': 'RecaptchaV2TaskProxyless',
                'websiteURL': page_url,
                'websiteKey': _sitekey,
            },
        }).encode()
        req = _urlreq.Request(f'{_api}/createTask', data=body,
                              headers={'Content-Type': 'application/json'})
        with _urlreq.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        if data.get('errorId', 1) != 0:
            print(f'    ⚠️  anti-captcha createTask: {data.get("errorDescription")}')
            return None
        task_id = data['taskId']
        print(f'    🔐 anti-captcha: задача #{task_id}, ждём решения...')

        result_body = json.dumps({'clientKey': ANTICAPTCHA_KEY, 'taskId': task_id}).encode()
        for i in range(24):
            time.sleep(5)
            req2 = _urlreq.Request(f'{_api}/getTaskResult', data=result_body,
                                   headers={'Content-Type': 'application/json'})
            with _urlreq.urlopen(req2, timeout=20) as r:
                res = json.loads(r.read())
            if res.get('errorId', 0) != 0:
                print(f'    ⚠️  anti-captcha error: {res.get("errorDescription")}')
                return None
            if res.get('status') == 'ready':
                token = res.get('solution', {}).get('gRecaptchaResponse')
                if token:
                    print(f'    ✅ anti-captcha: решена (попытка {i+1})')
                    return token
        print('    ⚠️  anti-captcha timeout (120s)')
        return None
    except Exception as e:
        print(f'    ⚠️  anti-captcha exception: {e}')
        return None


def _get_session() -> requests.Session:
    global _sess, _session_created_at
    now = time.time()
    if _sess is None or (now - _session_created_at) > SESSION_TTL:
        if _sess:
            try: _sess.close()
            except: pass
        s = requests.Session()
        s.headers.update(_HEADERS)
        s.verify = False
        if PROXY_URL:
            s.proxies = {'http': PROXY_URL, 'https': PROXY_URL}
        _sess = s
        _session_created_at = now
        print('  🔄 Новая сессия (ротация IP прокси)')
    return _sess


def _fetch(url: str, timeout: int = 25) -> tuple[str, str] | tuple[None, None]:
    """Загрузить страницу. Возвращает (html, actual_url) или (None, None).
    При капче — пытается решить через anti-captcha.com."""
    global _sess
    for attempt in range(4):
        try:
            resp = _get_session().get(url, timeout=timeout, allow_redirects=True)
            resp.encoding = 'utf-8'
            actual_url = resp.url  # URL после всех редиректов

            # Капча / блокировка
            is_captcha = ('showcaptcha' in actual_url or resp.status_code == 403
                          or (resp.status_code == 200
                              and 'showcaptcha' in resp.text[:500].lower()))
            if is_captcha:
                print(f'    ⚠️  Капча обнаружена (попытка {attempt+1}): {actual_url[:80]}')
                _sess = None  # сменить IP
                if ANTICAPTCHA_KEY:
                    token = _solve_anticaptcha(url)
                    if token:
                        sess = _get_session()
                        sess.cookies.set('g-recaptcha-response', token)
                        continue
                time.sleep(5 * (attempt + 1))
                continue

            if resp.status_code == 404:
                print(f'    ⚠️  404: {url}')
                return None, None

            if resp.status_code == 200 and len(resp.text) > 5000:
                return resp.text, actual_url

            print(f'    ⚠️  HTTP {resp.status_code}, len={len(resp.text)} (попытка {attempt+1})')
        except requests.exceptions.ProxyError:
            print(f'    ⚠️  ProxyError (попытка {attempt+1})')
            _sess = None
        except Exception as e:
            print(f'    ⚠️  {type(e).__name__}: {e} (попытка {attempt+1})')
        time.sleep(2.5 * (attempt + 1))
    return None, None


# ─── Извлечение данных со страницы ───────────────────────────────────────────

_CITY_SFXS = re.compile(
    r'-(krasnodar|maykop|sochi|anapa|gelendzhik|novorossiysk|armavir|'
    r'adygeysk|stavropol|rostov|volgograd|moscow|spb)$'
)


def _extract_photos(text: str, jk_url: str) -> list[str]:
    """Именованные -jk- фото с CDN CIAN (поддерживает 1–4 уровня субдиректорий).

    Логика:
    1. Сначала пробуем slug-фильтр — берём только фото именно этого ЖК.
    2. Если 0 — fallback: берём первые N уникальных -jk- фото со страницы
       (на странице конкретного ЖК в начале страницы лежат именно его фото).
    """
    slug_m = re.search(r'zhk-(.+?)-i\.cian\.ru', jk_url)
    jk_slug_full = slug_m.group(1).lower() if slug_m else ''
    jk_slug_key  = _CITY_SFXS.sub('', jk_slug_full).replace('-', '')

    def slug_ok(img: str) -> bool:
        low = re.sub(r'[^a-z0-9]', '', img.lower())
        return bool(jk_slug_key) and jk_slug_key in low

    raw = re.findall(
        r'images\.cdn-cian\.ru/images/(?:[0-9]+/)*'
        r'[a-zA-Z0-9_-]+-jk-[0-9]+-[0-9]+\.jpg',
        text
    )

    def normalise(img: str) -> str:
        base = re.sub(r'-[0-9]+\.jpg$', '-1.jpg', img)
        return 'https://' + base

    # ── Шаг 1: строгий slug-фильтр ────────────────────────────────────────────
    photos, seen = [], set()
    for img in raw:
        if not slug_ok(img):
            continue
        full = normalise(img)
        if full not in seen:
            seen.add(full)
            photos.append(full)

    # ── Шаг 2: fallback — первые unique -jk- фото из верхней части страницы ──
    if not photos:
        # Ищем только в первых ~400 KB HTML (галерея ЖК всегда в начале)
        for img in raw[:80]:
            full = normalise(img)
            if full not in seen:
                seen.add(full)
                photos.append(full)
            if len(photos) >= 10:
                break

    return photos[:30]


# Bounds берём из city_config.json для конкретного города; fallback — вся Россия
def _get_coord_bounds(city_id: int) -> tuple[float, float, float, float]:
    cfg = _CITY_CONFIG.get(str(city_id), {})
    return (
        float(cfg.get('lat_min', 40.0)),
        float(cfg.get('lat_max', 80.0)),
        float(cfg.get('lon_min', 19.0)),
        float(cfg.get('lon_max', 190.0)),
    )

_LAT_MIN, _LAT_MAX, _LON_MIN, _LON_MAX = _get_coord_bounds(1)   # обновляется в main()

_CIAN_FAKE_COORD = (44.609139, 37.6213)  # CIAN placeholder для «координаты неизвестны»


def _extract_coords(text: str) -> tuple[float | None, float | None]:
    """Координаты ЖК, строго в границах Краснодарского края/Адыгеи.
    Приоритет: вложенный объект \"coordinates\":{\"lat\":...} — самый надёжный из CIAN."""
    def _in_range(lat, lon):
        if abs(lat - _CIAN_FAKE_COORD[0]) < 0.001 and abs(lon - _CIAN_FAKE_COORD[1]) < 0.001:
            return False  # CIAN-заглушка «координаты неизвестны»
        return _LAT_MIN <= lat <= _LAT_MAX and _LON_MIN <= lon <= _LON_MAX

    # 1. Предпочитаем вложенный geo-объект {"lat":XX,"lng":YY} — максимально точно
    for m in re.finditer(
        r'"(?:coordinates|geoPoint|point|geo)"\s*:\s*\{[^}]*?"lat(?:itude)?"\s*:\s*([\d.]+)[^}]*?"(?:lng|lon(?:gitude)?)"\s*:\s*([\d.]+)',
        text
    ):
        lat, lon = float(m.group(1)), float(m.group(2))
        if _in_range(lat, lon):
            return lat, lon

    # 2. Пара на одной строке: latitude=XX&longitude=YY (URL-encoded в атрибутах)
    for m in re.finditer(
        r'lat(?:itude)?[=:]([0-9.]+)[^0-9.]{1,20}?lon(?:gitude)?[=:]([0-9.]+)',
        text
    ):
        lat, lon = float(m.group(1)), float(m.group(2))
        if _in_range(lat, lon):
            return lat, lon

    # 3. Fallback: все вхождения "lat":... и "lng":... по отдельности (только в диапазоне)
    lats = [float(x) for x in re.findall(r'"lat(?:itude)?"\s*:\s*([\d.]+)', text)
            if _LAT_MIN <= float(x) <= _LAT_MAX]
    lons = [float(x) for x in re.findall(r'"(?:lng|lon(?:gitude)?)"\s*:\s*([\d.]+)', text)
            if _LON_MIN <= float(x) <= _LON_MAX]
    return (lats[0] if lats else None, lons[0] if lons else None)


def _extract_description(text: str) -> str | None:
    """
    Описание ЖК. Приоритет:
    1. data-testid="AboutDescription" — официальный HTML-блок
    2. JSON-поля "description" / "about" с unicode-escapes (\u003C → <)
    3. Параграфы HTML вокруг 'AboutSection'
    """
    about = _parse_about_description(text)
    if about and len(about) > 80:
        return about[:6000]

    for pat in [
        r'"description"\s*:\s*"((?:[^"\\]|\\.){100,}?)"(?=[,}\]])',
        r'"about"\s*:\s*"((?:[^"\\]|\\.){100,}?)"(?=[,}\]])',
        r'"longDescription"\s*:\s*"((?:[^"\\]|\\.){100,}?)"(?=[,}\]])',
    ]:
        for raw in re.findall(pat, text, re.DOTALL):
            decoded = _safe_decode(raw)  # декодирует \u003C, убирает HTML-теги
            if (len(decoded) > 100
                    and re.search(r'[а-яА-Я]', decoded)
                    and 'Информация от официального' not in decoded
                    and 'Рейтинг основан' not in decoded
                    and not decoded.startswith('✅')):
                # Дополнительная очистка HTML-энтити
                decoded = html_lib.unescape(decoded)
                return decoded[:6000]

    # HTML-параграфы
    for anchor in ['AboutDescription', 'AboutSection', 'about-section', 'jk-about']:
        idx = text.find(anchor)
        if idx < 0:
            continue
        chunk = text[idx: idx + 8000]
        paras = [_strip_html(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', chunk, re.DOTALL)]
        paras = [p for p in paras if len(p) > 30]
        if paras:
            return '\n\n'.join(paras[:10])[:6000]
    return None


def _extract_developer_info(text: str) -> dict:
    result = {}
    m = re.search(r'"developerName"\s*:\s*"([^"]{2,150})"', text)
    if m:
        result['name'] = _safe_decode(m.group(1))
    m2 = re.search(r'"developerId"\s*:\s*([0-9]+)', text)
    if m2:
        result['cian_id'] = int(m2.group(1))
    m3 = re.search(r'cian\.ru/(zastroishchik-[a-z0-9-]+-[0-9]+)', text)
    if m3:
        result['url'] = 'https://cian.ru/' + m3.group(1)
    logo = _parse_logo_url(text)
    if logo:
        result['logo'] = logo
    return result


_ADDR_SKIP = {
    'россия', 'краснодарский край', 'республика адыгея', 'ставропольский край',
    'ростовская область', 'москва', 'санкт-петербург', 'краснодар', 'сочи',
    'республика алтай', 'алтайский край', 'новосибирск', 'новосибирская область',
}

def _extract_address(text: str) -> str | None:
    """Адрес ЖК — ищем fullAddress или собираем из fullName-компонентов страницы ЖК."""
    # Берём первый fullAddress — он обычно в верху JSON-данных страницы
    m = re.search(r'"fullAddress"\s*:\s*"([^"]{5,200})"', text)
    if m:
        addr = _safe_decode(m.group(1))
        # Отфильтровываем адреса из других городов
        if re.search(r'краснода|сочи|адыге', addr, re.I):
            return addr

    # Из fullName-компонентов: берём только первое вхождение (до первого повтора)
    raw_parts = re.findall(r'"fullName"\s*:\s*"([^"]{3,120})"', text)
    parts, seen = [], set()
    for p in raw_parts[:20]:   # первые 20 — обычно данные текущей страницы
        d = _safe_decode(p)
        key = d.lower().strip()
        if key in _ADDR_SKIP or d in seen:
            continue
        seen.add(d)
        parts.append(d)
        # Стоп как только встретили второй город — это уже навигация
        if len(parts) >= 4:
            break
    if parts:
        joined = ', '.join(parts)
        # Убеждаемся что адрес относится к нашему региону
        if not re.search(r'краснода|сочи|адыге|кубань', joined, re.I):
            return None
        return joined
    return None


# ─── Обработка одного ЖК ─────────────────────────────────────────────────────

def process_jk(cur, conn, rc_id: int, rc_name: str, rc_slug: str,
               cian_id: int | None, dev_cache: dict, force: bool = False) -> dict:
    result = {'rc_id': rc_id, 'name': rc_name, 'status': 'skip'}

    # ── 1. Данные из Phase-1 кэша ──────────────────────────────────────────────
    cache_key  = str(cian_id) if cian_id else ''
    cache_data = _JK_CACHE.get(cache_key, {})
    cache_url  = cache_data.get('jk_url', '')

    # Список URL для попытки (порядок важен — первый успешный побеждает)
    _city_sfxs = ['krasnodar', 'sochi', 'anapa', 'gelendzhik', 'novorossiysk',
                  'maykop', 'armavir', 'novorossiysk', 'krasnodar-kray']
    urls_to_try: list[str] = []
    if cache_url:
        urls_to_try.append(cache_url)
    if rc_slug:
        # С городским суффиксом (нужен для большинства краснодарских ЖК)
        for city in _city_sfxs:
            candidate = f'https://zhk-{rc_slug}-{city}-i.cian.ru/'
            if candidate not in urls_to_try:
                urls_to_try.append(candidate)
        # Без суффикса — запасной вариант
        bare = f'https://zhk-{rc_slug}-i.cian.ru/'
        if bare not in urls_to_try:
            urls_to_try.append(bare)
    # Редирект CIAN по ID — работает для всех, последний шанс
    if cian_id:
        cian_redirect = f'https://www.cian.ru/zhilye-kompleksy/{cian_id}/'
        if cian_redirect not in urls_to_try:
            urls_to_try.append(cian_redirect)

    # ── 2. Загрузка страницы ЖК ───────────────────────────────────────────────
    text = None
    final_url = ''
    for url in urls_to_try:
        t, actual_url = _fetch(url)
        if t and len(t) > 8000:
            # Убеждаемся что это страница ЖК, а не главная/поиск
            if 'zhk-' in (actual_url or url).lower() or 'newbuilding' in t[:2000].lower() or 'ЖК' in t[:3000]:
                text = t
                final_url = actual_url or url  # используем URL после редиректа
                break
        time.sleep(REQ_DELAY * 0.5)

    # ── 3. Извлечение данных ──────────────────────────────────────────────────
    # Фото: только из страницы
    photos: list[str] = []
    if text:
        photos = _extract_photos(text, final_url)

    # Координаты: сначала страница, потом кэш (там нет coords — заглушка)
    lat = lon = None
    if text:
        lat, lon = _extract_coords(text)

    # Описание: из страницы
    desc: str | None = None
    if text:
        desc = _extract_description(text)

    # Адрес: страница → кэш
    addr: str | None = None
    if text:
        addr = _extract_address(text)
    if not addr and cache_data.get('address'):
        addr = cache_data['address']

    # Материал стен: страница → кэш
    material: str | None = None
    if text:
        m = re.search(r'"materialType"\s*:\s*"([^"]{3,80})"', text)
        if not m:
            m = re.search(r'"materials"\s*:\s*\["([^"]{3,80})"', text)
        material = _safe_decode(m.group(1)) if m else None
    if not material and cache_data.get('wall_material'):
        material = cache_data['wall_material']

    # Класс объекта: страница → кэш
    obj_cls: str | None = None
    if text:
        m2 = re.search(r'"newbuildingClass"\s*:\s*"([^"]{2,40})"', text)
        obj_cls = _safe_decode(m2.group(1)) if m2 else None
    if not obj_cls and cache_data.get('object_class'):
        obj_cls = cache_data['object_class']

    # Сроки сдачи: страница → кэш
    end_yr = end_q = None
    if text:
        for pat in [r'([1-4])\s*кв[^0-9]*([0-9]{4})',
                    r'"deliveryDate"\s*:\s*"([^"]+)"']:
            fm = re.search(pat, text)
            if fm:
                try:
                    end_yr = int(fm.group(2)); end_q = int(fm.group(1))
                except: pass
                break
    if not end_yr and cache_data.get('end_build_year'):
        end_yr = cache_data['end_build_year']
        end_q  = cache_data.get('end_build_quarter')

    # Логотип + варианты отделки
    logo   = _parse_logo_url(text) if text else None
    finish = _parse_finishing_variants(text) if text else None

    # Количество корпусов: из houseId на странице → fallback на distinct имена в properties
    buildings_count: int | None = None
    if text:
        # Шаг 1: считаем уникальные houseId — самый надёжный источник
        house_ids = list(dict.fromkeys(re.findall(r'"houseId"\s*:\s*(\d+)', text)))
        if house_ids:
            buildings_count = len(house_ids)
        else:
            # Шаг 2: поле buildingsCount в JSON страницы
            bc_m = re.search(r'"buildingsCount"\s*:\s*([0-9]+)', text)
            if bc_m:
                buildings_count = int(bc_m.group(1))
    if not buildings_count:
        # Шаг 3: COUNT DISTINCT из таблицы свойств
        cur.execute(
            "SELECT COUNT(DISTINCT complex_building_name) FROM properties "
            "WHERE complex_id=%s AND is_active=TRUE "
            "AND complex_building_name IS NOT NULL AND complex_building_name!=''",
            (rc_id,)
        )
        _db_cnt = (cur.fetchone() or [0])[0]
        if _db_cnt and _db_cnt > 0:
            buildings_count = _db_cnt

    # ── 4. Застройщик ─────────────────────────────────────────────────────────
    # Приоритет: страница → кэш (dev_name + builder_id)
    dev_info: dict = {}
    if text:
        dev_info = _extract_developer_info(text)
    if not dev_info.get('name') and cache_data.get('dev_name'):
        dev_info['name']    = cache_data['dev_name']
        dev_info['cian_id'] = cache_data.get('builder_id')
    if not dev_info.get('url') and cache_data.get('dev_profile_uri'):
        dev_info['url'] = cache_data['dev_profile_uri']

    developer_id: int | None = None
    if dev_info.get('name') or dev_info.get('cian_id'):
        developer_id = get_or_create_developer(
            cur,
            name=dev_info.get('name', ''),
            dev_cache=dev_cache,
            cian_id=dev_info.get('cian_id'),
        )
        if developer_id and dev_info.get('url'):
            cur.execute(
                "UPDATE developers SET source_url=%s, updated_at=NOW() "
                "WHERE id=%s AND (source_url IS NULL OR source_url='')",
                (dev_info['url'], developer_id)
            )
        if developer_id and dev_info.get('logo'):
            cur.execute(
                "UPDATE developers SET logo_url=%s, updated_at=NOW() "
                "WHERE id=%s AND (logo_url IS NULL OR logo_url='')",
                (dev_info['logo'], developer_id)
            )

    # ── 5. UPDATE БД ─────────────────────────────────────────────────────────
    # Получаем текущие значения чтобы не затирать имеющиеся данные
    cur.execute("""
        SELECT main_image, latitude, longitude, address, developer_id, description
        FROM residential_complexes WHERE id=%s
    """, (rc_id,))
    cur_row = cur.fetchone() or (None,)*6
    cur_photo, cur_lat, cur_lon, cur_addr, cur_dev_id, cur_desc = cur_row

    fields, values = [], []

    def add(col, val):
        if val is not None:
            fields.append(col); values.append(val)

    # Фото: записываем всегда если нашли (качество данных важнее)
    if photos:
        add('main_image', photos[0][:499])
        add('gallery_images', json.dumps(photos[:20], ensure_ascii=False))
    # Координаты: только если ещё нет (или force)
    if lat and (force or not cur_lat):   add('latitude',  lat)
    if lon and (force or not cur_lon):   add('longitude', lon)
    # Описание: перезаписываем только если новое длиннее
    if desc and (force or not cur_desc or len(desc) > len(cur_desc or '')):
        add('description', desc[:4999])
    # Адрес: только если ещё нет
    if addr and (force or not cur_addr): add('address', addr[:299])
    if material: add('wall_material', material[:99])
    if obj_cls:  add('object_class_display_name', obj_cls[:49])
    if end_yr:   add('end_build_year', end_yr)
    if end_q:    add('end_build_quarter', end_q)
    if logo:     add('logo_url', logo[:499])
    if finish:   add('finishing_variants', finish[:1999])
    if buildings_count: add('buildings_count', buildings_count)
    # Застройщик: не перезаписываем если уже привязан (кроме force)
    if developer_id and (force or not cur_dev_id):
        add('developer_id', developer_id)
    if cian_id:  add('complex_id', cian_id)
    add('updated_at', datetime.now())

    if fields:
        sql = (
            f"UPDATE residential_complexes "
            f"SET {', '.join(f + '=%s' for f in fields)} "
            f"WHERE id=%s"
        )
        cur.execute(sql, values + [rc_id])
        conn.commit()

    fetched = text is not None
    result.update({
        'status':       'ok',
        'fetched':      fetched,
        'from_cache':   bool(cache_data),
        'photos':       len(photos),
        'lat':          lat,
        'lon':          lon,
        'desc_len':     len(desc) if desc else 0,
        'addr':         addr,
        'developer':    dev_info.get('name'),
        'developer_id': developer_id,
        'fields':       len(fields),
    })
    return result


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='Bulk JK enrichment from CIAN')
    ap.add_argument('--city',  type=int, default=1)
    ap.add_argument('--limit', type=int, default=0, help='0 = все')
    ap.add_argument('--id',    type=str, default='', help='rc IDs через запятую')
    ap.add_argument('--force', action='store_true',
                    help='обновить даже ЖК у которых уже есть данные')
    args = ap.parse_args()

    # Загружаем глобальный кэш Phase-1 для нужного города
    global _JK_CACHE
    _JK_CACHE = _load_jk_cache(args.city)

    # Имя города из конфига + обновляем координатные bounds для этого города
    city_cfg  = _CITY_CONFIG.get(str(args.city), {})
    city_name = city_cfg.get('name', f'city_id={args.city}')
    global _LAT_MIN, _LAT_MAX, _LON_MIN, _LON_MAX
    _LAT_MIN, _LAT_MAX, _LON_MIN, _LON_MAX = _get_coord_bounds(args.city)
    print(f'🏙️  Город: {city_name} | cache JKs: {len(_JK_CACHE)}')

    conn = psycopg2.connect(
        host=os.environ.get('PGHOST'),
        database=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER', 'postgres'),
        password=os.environ.get('PGPASSWORD', ''),
    )
    cur = conn.cursor()
    dev_cache: dict = {}

    # ── Целевой список ЖК ─────────────────────────────────────────────────────
    if args.id:
        ids = [int(x) for x in args.id.split(',')]
        cur.execute("""
            SELECT rc.id, rc.name, rc.slug, rc.complex_id
            FROM residential_complexes rc
            WHERE rc.id = ANY(%s)
            ORDER BY rc.name
        """, (ids,))
    elif args.force:
        q = """
            SELECT rc.id, rc.name, rc.slug, rc.complex_id
            FROM residential_complexes rc
            WHERE rc.city_id = %s AND rc.complex_id IS NOT NULL
            ORDER BY rc.name
        """
        cur.execute(q + (f" LIMIT {args.limit}" if args.limit else ''), (args.city,))
    else:
        q = """
            SELECT rc.id, rc.name, rc.slug, rc.complex_id
            FROM residential_complexes rc
            WHERE rc.city_id = %s
              AND rc.complex_id IS NOT NULL
              AND (rc.main_image IS NULL
                   OR rc.latitude     IS NULL
                   OR rc.address      IS NULL
                   OR rc.developer_id IS NULL
                   OR rc.description  IS NULL)
            ORDER BY rc.main_image NULLS FIRST, rc.name
        """
        cur.execute(q + (f" LIMIT {args.limit}" if args.limit else ''), (args.city,))

    rows = cur.fetchall()
    total = len(rows)
    print(f'\n🔍 ЖК для обработки: {total}\n{"═"*60}')
    if not total:
        print('Нет ЖК с недостающими данными — всё уже заполнено!')
        return

    ok = fail = skip = 0
    t0 = time.time()

    for i, (rc_id, rc_name, slug, cian_id) in enumerate(rows, 1):
        elapsed = time.time() - t0
        eta_s   = (elapsed / i) * (total - i) if i > 1 else 0
        print(f'\n[{i}/{total}] {rc_name} (id={rc_id}, cian={cian_id}) '
              f'| ETA {eta_s/60:.0f}м{eta_s%60:.0f}с')

        try:
            res = process_jk(cur, conn, rc_id, rc_name, slug or '',
                             cian_id, dev_cache, force=args.force)
        except Exception as e:
            import traceback; traceback.print_exc()
            conn.rollback()
            res = {'status': 'error', 'error': str(e)}

        if res['status'] == 'ok':
            ok += 1
            icon = '✅' if res['fetched'] else '📦'
            lat_str = f'{res["lat"]:.4f}' if res["lat"] else '—'
            addr_str = str(res["addr"])[:45] if res["addr"] else '—'
            print(f'  {icon} фото={res["photos"]}  lat={lat_str}  '
                  f'addr={addr_str}  dev={res["developer"] or "—"}  '
                  f'desc={res["desc_len"]}c  ({res["fields"]} полей)')
        elif res['status'] in ('fetch_failed', 'error'):
            fail += 1
            print(f'  ❌ {res.get("error", "fetch failed")}')
        else:
            skip += 1

        time.sleep(REQ_DELAY)

    conn.close()
    elapsed_total = time.time() - t0
    print(f'\n{"═"*60}')
    print(f'Итого: ✅{ok}  ❌{fail}  ⏭️{skip}  из {total} ЖК  '
          f'за {elapsed_total/60:.1f} мин')


if __name__ == '__main__':
    main()
