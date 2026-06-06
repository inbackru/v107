import { useEffect, useRef, useState } from "react";

const EVENTS = [
  {
    type: "booking",
    icon: "🏠",
    label: "Забронировал квартиру",
    name: "Александр К.",
    complex: "ЖК «Южный»",
    detail: "3-комн., 89 м²",
    price: "9 400 000 ₽",
    cashback: "470 000 ₽",
    img: "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=600&q=80",
    color: "#0088CC",
    badge: "Бронирование",
    badgeBg: "rgba(0,136,204,0.12)",
    badgeColor: "#0088CC",
  },
  {
    type: "mortgage",
    icon: "✅",
    label: "Одобрили ипотеку",
    name: "Елена В.",
    complex: "ЖК «Парковый»",
    detail: "2-комн., 62 м²",
    price: "6 100 000 ₽",
    cashback: "305 000 ₽",
    img: "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=600&q=80",
    color: "#16a34a",
    badge: "Ипотека одобрена",
    badgeBg: "rgba(22,163,74,0.12)",
    badgeColor: "#16a34a",
  },
  {
    type: "deal",
    icon: "🎉",
    label: "Сделка состоялась",
    name: "Дмитрий М.",
    complex: "ЖК «Престиж»",
    detail: "1-комн., 44 м²",
    price: "4 850 000 ₽",
    cashback: "242 500 ₽",
    img: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&q=80",
    color: "#d97706",
    badge: "Сделка",
    badgeBg: "rgba(217,119,6,0.12)",
    badgeColor: "#d97706",
  },
  {
    type: "cashback",
    icon: "💰",
    label: "Получил кэшбек",
    name: "Анна Р.",
    complex: "ЖК «Горизонт»",
    detail: "2-комн., 71 м²",
    price: "7 200 000 ₽",
    cashback: "360 000 ₽",
    img: "https://images.unsplash.com/photo-1460317442991-0ec209397118?w=600&q=80",
    color: "#7c3aed",
    badge: "Кэшбек выплачен",
    badgeBg: "rgba(124,58,237,0.12)",
    badgeColor: "#7c3aed",
  },
];

export function VariantA() {
  const [current, setCurrent] = useState(0);
  const [animating, setAnimating] = useState(false);
  const [prevIdx, setPrevIdx] = useState<number | null>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setPrevIdx(current);
      setAnimating(true);
      setTimeout(() => {
        setCurrent((c) => (c + 1) % EVENTS.length);
        setAnimating(false);
        setPrevIdx(null);
      }, 500);
    }, 3500);
    return () => clearInterval(timer);
  }, [current]);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    setTilt({ x: y * 14, y: x * -14 });
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
    setTilt({ x: 0, y: 0 });
  };

  const ev = EVENTS[current];

  return (
    <div className="min-h-screen bg-white flex items-center" style={{ fontFamily: "'Inter', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(24px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideDown {
          from { opacity: 1; transform: translateY(0); }
          to { opacity: 0; transform: translateY(-24px); }
        }
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(0.85); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(-1deg); }
          50% { transform: translateY(-10px) rotate(1deg); }
        }
        @keyframes shimmer {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        @keyframes badgeIn {
          from { opacity: 0; transform: translateX(-12px) scale(0.95); }
          to { opacity: 1; transform: translateX(0) scale(1); }
        }
        .gradient-text {
          background: linear-gradient(135deg, #0088CC 0%, #0064a8 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .event-in { animation: slideUp 0.5s cubic-bezier(0.34,1.56,0.64,1) forwards; }
        .event-out { animation: slideDown 0.5s ease-in forwards; }
        .card-float { animation: float 6s ease-in-out infinite; }
        .badge-in { animation: badgeIn 0.4s cubic-bezier(0.34,1.56,0.64,1) forwards; }
        .live-dot { animation: pulse-dot 1.4s ease-in-out infinite; }
        .stat-shimmer {
          background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
          background-size: 200% auto;
        }
      `}</style>

      <div className="w-full max-w-6xl mx-auto px-6 py-12">
        <div className="grid grid-cols-5 gap-10 items-center">
          {/* LEFT */}
          <div className="col-span-2 space-y-6">
            <div className="inline-flex items-center gap-2 bg-blue-50 px-3 py-1.5 rounded-full text-xs font-semibold text-[#0088CC]">
              <span className="live-dot w-2 h-2 rounded-full bg-green-500 inline-block"></span>
              LIVE · Платформа активна сейчас
            </div>

            <h1 className="text-4xl xl:text-5xl font-extrabold text-gray-900 leading-tight tracking-tight">
              Выгода до{" "}
              <span className="gradient-text whitespace-nowrap">500 000 ₽</span>
              <br />
              при покупке{" "}
              <span className="gradient-text">квартиры</span>
              <br />в Краснодаре
            </h1>

            <p className="text-gray-500 text-lg font-medium leading-relaxed">
              Платформа для выгодных покупок новостроек в России
            </p>

            <div className="bg-white rounded-2xl p-1.5 shadow-xl border border-gray-100">
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

            <div className="flex items-center gap-8 pt-1">
              <div>
                <div className="text-3xl font-extrabold text-gray-900">53 844</div>
                <div className="text-xs text-gray-400 font-medium mt-0.5">квартир в каталоге</div>
              </div>
              <div className="w-px h-10 bg-gray-100"></div>
              <div>
                <div className="text-3xl font-extrabold text-gray-900">328</div>
                <div className="text-xs text-gray-400 font-medium mt-0.5">жилых комплексов</div>
              </div>
              <div className="w-px h-10 bg-gray-100"></div>
              <div>
                <div className="flex text-yellow-400 text-sm mb-0.5">★★★★★</div>
                <div className="text-sm font-bold text-gray-900">4.9<span className="text-gray-400 font-normal text-xs">/5 рейтинг</span></div>
              </div>
            </div>
          </div>

          {/* RIGHT — 3D CARD */}
          <div className="col-span-3 flex items-center justify-center">
            <div className="relative w-full max-w-lg" style={{ perspective: "1200px" }}>

              {/* Glow under card */}
              <div
                className="absolute inset-x-8 bottom-0 h-16 rounded-3xl blur-2xl transition-all duration-700"
                style={{ background: ev.color, opacity: 0.25, transform: "translateY(24px)" }}
              />

              {/* 3D Card */}
              <div
                ref={cardRef}
                className="relative rounded-3xl overflow-hidden shadow-2xl cursor-pointer card-float"
                style={{
                  transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale(${isHovering ? 1.02 : 1})`,
                  transition: isHovering ? "transform 0.1s ease" : "transform 0.6s cubic-bezier(0.25,0.46,0.45,0.94)",
                  transformStyle: "preserve-3d",
                  minHeight: 460,
                }}
                onMouseMove={handleMouseMove}
                onMouseEnter={() => setIsHovering(true)}
                onMouseLeave={handleMouseLeave}
              >
                {/* BG image */}
                <div className="absolute inset-0">
                  <img
                    key={ev.img}
                    src={ev.img}
                    alt={ev.complex}
                    className="w-full h-full object-cover transition-transform duration-700"
                    style={{ transform: isHovering ? "scale(1.04)" : "scale(1)" }}
                  />
                  <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.05) 100%)" }} />
                </div>

                {/* TOP badge */}
                <div className="absolute top-5 left-5 right-5 flex items-start justify-between" style={{ transform: "translateZ(40px)" }}>
                  <div
                    key={ev.badge}
                    className="badge-in flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold backdrop-blur-md"
                    style={{ background: "rgba(255,255,255,0.92)", color: ev.color, boxShadow: "0 2px 12px rgba(0,0,0,0.12)" }}
                  >
                    <span>{ev.icon}</span>
                    <span>{ev.badge}</span>
                  </div>
                  <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full backdrop-blur-md" style={{ background: "rgba(0,0,0,0.35)" }}>
                    <span className="live-dot w-1.5 h-1.5 rounded-full bg-red-400 inline-block"></span>
                    <span className="text-white text-xs font-bold tracking-wide">LIVE</span>
                  </div>
                </div>

                {/* BOTTOM info */}
                <div className="absolute bottom-0 left-0 right-0 p-6" style={{ transform: "translateZ(40px)" }}>
                  <div
                    key={current + "-info"}
                    className={animating ? "event-out" : "event-in"}
                  >
                    <div className="text-white/70 text-xs font-medium mb-1">{ev.name} · только что</div>
                    <div className="text-white text-xl font-bold mb-0.5">{ev.complex}</div>
                    <div className="text-white/80 text-sm mb-4">{ev.detail} · {ev.price}</div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="text-white/60 text-xs">Кэшбек</div>
                        <div
                          className="text-white text-sm font-extrabold px-3 py-1 rounded-lg"
                          style={{ background: "rgba(255,255,255,0.15)", backdropFilter: "blur(8px)" }}
                        >
                          +{ev.cashback}
                        </div>
                      </div>
                      <div className="flex gap-1.5">
                        {EVENTS.map((_, i) => (
                          <button
                            key={i}
                            onClick={() => setCurrent(i)}
                            className="rounded-full transition-all duration-300"
                            style={{
                              width: i === current ? 20 : 6,
                              height: 6,
                              background: i === current ? "#fff" : "rgba(255,255,255,0.35)",
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Shine overlay */}
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    background: `radial-gradient(ellipse at ${50 + tilt.y * 5}% ${50 + tilt.x * 5}%, rgba(255,255,255,0.08) 0%, transparent 70%)`,
                    transition: isHovering ? "background 0.1s" : "background 0.6s",
                  }}
                />
              </div>

              {/* Floating cashback badge */}
              <div
                className="absolute -right-4 top-8 px-4 py-2 rounded-2xl shadow-xl backdrop-blur-sm border border-white/40"
                style={{ background: "rgba(255,255,255,0.95)", transform: "translateZ(60px)", zIndex: 10 }}
              >
                <div className="text-xs text-gray-500 font-medium">Сэкономлено</div>
                <div className="text-[#0088CC] font-extrabold text-lg leading-tight">10 млн+ ₽</div>
              </div>

              {/* Floating event notification */}
              <div
                key={current + "-notif"}
                className="absolute -left-6 bottom-16 flex items-center gap-3 px-4 py-3 rounded-2xl shadow-xl event-in"
                style={{ background: "rgba(255,255,255,0.97)", backdropFilter: "blur(12px)", border: "1px solid rgba(0,0,0,0.06)", minWidth: 220, zIndex: 10 }}
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
                  style={{ background: ev.badgeBg }}
                >
                  {ev.icon}
                </div>
                <div>
                  <div className="text-xs font-semibold text-gray-800">{ev.label}</div>
                  <div className="text-xs text-gray-400 mt-0.5">{ev.complex} · 1 мин назад</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
