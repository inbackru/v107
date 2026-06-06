import { useEffect, useRef, useState } from "react";

const COMPLEXES = [
  {
    img: "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=300&q=80",
    name: "ЖК «Южный»",
    district: "Прикубанский р-н",
  },
  {
    img: "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=300&q=80",
    name: "ЖК «Парковый»",
    district: "Карасунский р-н",
  },
  {
    img: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=300&q=80",
    name: "ЖК «Престиж»",
    district: "Западный р-н",
  },
  {
    img: "https://images.unsplash.com/photo-1460317442991-0ec209397118?w=300&q=80",
    name: "ЖК «Горизонт»",
    district: "Центральный р-н",
  },
  {
    img: "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=300&q=80",
    name: "ЖК «Сенатор»",
    district: "Прикубанский р-н",
  },
];

type EventType = "booking" | "mortgage" | "deal" | "cashback" | "view";

const EVENT_TEMPLATES: Array<{
  type: EventType;
  icon: string;
  label: string;
  badgeText: string;
  badgeColor: string;
  badgeBg: string;
  dotColor: string;
  names: string[];
  detailFn: () => string;
  subFn: () => string;
}> = [
  {
    type: "booking",
    icon: "🏠",
    label: "Забронировал квартиру",
    badgeText: "Бронирование",
    badgeColor: "#0088CC",
    badgeBg: "rgba(0,136,204,0.1)",
    dotColor: "#0088CC",
    names: ["Александр К.", "Михаил С.", "Владимир Н.", "Сергей П."],
    detailFn: () => `${["1", "2", "3", "2"][Math.floor(Math.random() * 4)]}-комн., ${[44, 62, 75, 89][Math.floor(Math.random() * 4)]} м²`,
    subFn: () => `${(Math.floor(Math.random() * 9) + 4)} 000 000 ₽`,
  },
  {
    type: "mortgage",
    icon: "✅",
    label: "Одобрили ипотеку",
    badgeText: "Ипотека",
    badgeColor: "#16a34a",
    badgeBg: "rgba(22,163,74,0.1)",
    dotColor: "#16a34a",
    names: ["Елена В.", "Ольга М.", "Наталья Р.", "Ирина К."],
    detailFn: () => `Ставка ${[5.9, 6.1, 6.5, 7.2][Math.floor(Math.random() * 4)]}%`,
    subFn: () => `на ${[15, 20, 25, 30][Math.floor(Math.random() * 4)]} лет`,
  },
  {
    type: "deal",
    icon: "🤝",
    label: "Сделка состоялась",
    badgeText: "Сделка",
    badgeColor: "#d97706",
    badgeBg: "rgba(217,119,6,0.1)",
    dotColor: "#d97706",
    names: ["Дмитрий М.", "Алексей Т.", "Роман Б.", "Иван Г."],
    detailFn: () => `Кэшбек ${[242, 305, 390, 470][Math.floor(Math.random() * 4)]} 000 ₽`,
    subFn: () => "выплачен клиенту",
  },
  {
    type: "cashback",
    icon: "💰",
    label: "Кэшбек получен",
    badgeText: "Кэшбек",
    badgeColor: "#7c3aed",
    badgeBg: "rgba(124,58,237,0.1)",
    dotColor: "#7c3aed",
    names: ["Анна Р.", "Мария И.", "Светлана Д.", "Юлия Ф."],
    detailFn: () => `+${[180, 242, 305, 390][Math.floor(Math.random() * 4)]} 000 ₽`,
    subFn: () => "на счёт клиента",
  },
  {
    type: "view",
    icon: "👁",
    label: "Изучает предложения",
    badgeText: "Просмотр",
    badgeColor: "#64748b",
    badgeBg: "rgba(100,116,139,0.1)",
    dotColor: "#94a3b8",
    names: ["Павел С.", "Артём В.", "Никита О.", "Тимур Ш."],
    detailFn: () => `${[3, 5, 7, 12][Math.floor(Math.random() * 4)]} квартиры`,
    subFn: () => "сравнивает варианты",
  },
];

interface FeedEvent {
  id: number;
  template: typeof EVENT_TEMPLATES[0];
  complex: typeof COMPLEXES[0];
  name: string;
  detail: string;
  sub: string;
  timeAgo: string;
  entering: boolean;
}

let _id = 0;
function makeEvent(): FeedEvent {
  const t = EVENT_TEMPLATES[Math.floor(Math.random() * EVENT_TEMPLATES.length)];
  const c = COMPLEXES[Math.floor(Math.random() * COMPLEXES.length)];
  const mins = Math.floor(Math.random() * 4) + 1;
  return {
    id: _id++,
    template: t,
    complex: c,
    name: t.names[Math.floor(Math.random() * t.names.length)],
    detail: t.detailFn(),
    sub: t.subFn(),
    timeAgo: mins === 1 ? "1 мин назад" : `${mins} мин назад`,
    entering: true,
  };
}

const INITIAL: FeedEvent[] = Array.from({ length: 5 }, makeEvent).map((e) => ({ ...e, entering: false }));

export function VariantB() {
  const [feed, setFeed] = useState<FeedEvent[]>(INITIAL);
  const [counter, setCounter] = useState({ bookings: 127, mortgage: 43, deals: 89 });
  const feedRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setInterval(() => {
      const newEv = makeEvent();
      setFeed((prev) => [newEv, ...prev].slice(0, 7));
      setCounter((c) => ({
        bookings: c.bookings + (Math.random() > 0.6 ? 1 : 0),
        mortgage: c.mortgage + (Math.random() > 0.7 ? 1 : 0),
        deals: c.deals + (Math.random() > 0.75 ? 1 : 0),
      }));
    }, 2800);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-[#f8fafc] flex items-center" style={{ fontFamily: "'Inter', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        @keyframes slideInFeed {
          from { opacity: 0; transform: translateY(-20px) scale(0.97); max-height: 0; margin-top: 0; }
          to { opacity: 1; transform: translateY(0) scale(1); max-height: 120px; margin-top: 0; }
        }
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
          50% { opacity: 0.8; box-shadow: 0 0 0 6px rgba(34,197,94,0); }
        }
        @keyframes countUp {
          from { transform: translateY(8px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        @keyframes scanline {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(400%); }
        }
        .gradient-text {
          background: linear-gradient(135deg, #0088CC 0%, #0064a8 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .feed-item-new { animation: slideInFeed 0.4s cubic-bezier(0.34,1.3,0.64,1) forwards; }
        .live-dot { animation: pulse-dot 1.6s ease-in-out infinite; }
        .count-up { animation: countUp 0.3s ease-out forwards; }
      `}</style>

      <div className="w-full max-w-6xl mx-auto px-6 py-12">
        <div className="grid grid-cols-5 gap-12 items-center">

          {/* LEFT */}
          <div className="col-span-2 space-y-6">
            <div className="inline-flex items-center gap-2 bg-white border border-gray-200 px-3 py-1.5 rounded-full shadow-sm">
              <span className="live-dot w-2 h-2 rounded-full bg-green-400 inline-block"></span>
              <span className="text-xs font-semibold text-gray-700">Сейчас активно {counter.bookings + counter.deals} клиентов</span>
            </div>

            <h1 className="text-4xl xl:text-5xl font-extrabold text-gray-900 leading-tight tracking-tight">
              Выгода до{" "}
              <span className="gradient-text whitespace-nowrap">500 000 ₽</span>
              <br />
              при покупке{" "}
              <span className="gradient-text">квартиры</span>
              <br />в Краснодаре
            </h1>

            <p className="text-gray-500 text-lg font-medium">
              Платформа для выгодных покупок новостроек в России
            </p>

            <div className="bg-white rounded-2xl p-1.5 shadow-lg border border-gray-100">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Город, улица, ЖК, застройщик"
                  className="flex-grow px-5 py-3.5 rounded-xl text-sm outline-none text-gray-700 placeholder-gray-400"
                />
                <button
                  className="px-6 py-3.5 rounded-xl text-white text-sm font-semibold whitespace-nowrap transition-all hover:opacity-90 active:scale-95"
                  style={{ background: "linear-gradient(135deg,#0088CC,#0064a8)" }}
                >
                  Найти
                </button>
              </div>
            </div>

            {/* Live counters */}
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: "Бронирований", value: counter.bookings, color: "#0088CC", bg: "rgba(0,136,204,0.06)" },
                { label: "Ипотек", value: counter.mortgage, color: "#16a34a", bg: "rgba(22,163,74,0.06)" },
                { label: "Сделок", value: counter.deals, color: "#d97706", bg: "rgba(217,119,6,0.06)" },
              ].map((stat) => (
                <div
                  key={stat.label}
                  className="rounded-2xl p-3 text-center"
                  style={{ background: stat.bg }}
                >
                  <div
                    key={stat.value}
                    className="text-2xl font-extrabold count-up"
                    style={{ color: stat.color }}
                  >
                    {stat.value}
                  </div>
                  <div className="text-xs text-gray-500 font-medium mt-0.5">{stat.label}</div>
                  <div className="text-xs font-semibold mt-1" style={{ color: stat.color }}>сегодня</div>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-4 pt-1">
              <div className="flex text-yellow-400 text-sm">★★★★★</div>
              <div className="text-sm text-gray-600 font-medium">
                <span className="font-bold text-gray-900">4.9/5</span> · 53 844 квартиры · 328 ЖК
              </div>
            </div>
          </div>

          {/* RIGHT — LIVE EVENT FEED */}
          <div className="col-span-3">
            <div className="relative">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <div className="live-dot w-2.5 h-2.5 rounded-full bg-red-500 inline-block shadow-sm"></div>
                  <span className="text-sm font-bold text-gray-900 tracking-wide uppercase">Что происходит прямо сейчас</span>
                </div>
                <div className="text-xs text-gray-400 font-medium">обновляется в реальном времени</div>
              </div>

              {/* Feed */}
              <div ref={feedRef} className="space-y-2.5 overflow-hidden" style={{ maxHeight: 520 }}>
                {feed.map((ev, i) => (
                  <div
                    key={ev.id}
                    className={`flex items-center gap-4 bg-white rounded-2xl p-4 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200 ${i === 0 && ev.entering !== false ? "feed-item-new" : ""}`}
                    style={{ opacity: i > 4 ? 0.5 : 1 }}
                  >
                    {/* Complex image */}
                    <div className="relative flex-shrink-0 w-16 h-16 rounded-xl overflow-hidden">
                      <img src={ev.complex.img} alt={ev.complex.name} className="w-full h-full object-cover" />
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className="text-xs font-bold px-2.5 py-0.5 rounded-full"
                          style={{ color: ev.template.badgeColor, background: ev.template.badgeBg }}
                        >
                          {ev.template.icon} {ev.template.badgeText}
                        </span>
                        <span className="text-xs text-gray-400">{ev.timeAgo}</span>
                      </div>
                      <div className="text-sm font-semibold text-gray-900 truncate">{ev.complex.name}</div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-gray-500">{ev.name}</span>
                        <span className="text-gray-300">·</span>
                        <span className="text-xs text-gray-500">{ev.detail}</span>
                        <span className="text-gray-300">·</span>
                        <span className="text-xs font-medium" style={{ color: ev.template.badgeColor }}>{ev.sub}</span>
                      </div>
                    </div>

                    {/* Right dot */}
                    <div
                      className="flex-shrink-0 w-2 h-2 rounded-full"
                      style={{ background: i === 0 ? ev.template.dotColor : "#e2e8f0" }}
                    />
                  </div>
                ))}
              </div>

              {/* Bottom fade */}
              <div className="absolute bottom-0 left-0 right-0 h-16 pointer-events-none rounded-b-2xl" style={{ background: "linear-gradient(to top, #f8fafc, transparent)" }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
