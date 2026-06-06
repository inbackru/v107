import React from "react";
import { 
  ChevronRight, 
  Heart, 
  Share2, 
  MapPin, 
  Maximize2,
  Ruler,
  DoorOpen,
  ArrowUpToLine,
  Hammer,
  Calendar,
  Building,
  CheckCircle2,
  Phone,
  MessageCircle,
  Calculator,
  ShieldCheck,
  Star
} from "lucide-react";

export function LuxuryDark() {
  return (
    <>
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
        
        .font-serif {
          font-family: 'Playfair Display', serif;
        }
        
        .font-sans {
          font-family: 'Inter', sans-serif;
        }

        .bg-luxury-dark {
          background-color: #0A0C10;
        }

        .bg-luxury-panel {
          background-color: #12151C;
        }

        .text-gold {
          color: #D4AF37;
        }
        
        .bg-gold {
          background-color: #D4AF37;
        }
        
        .border-gold {
          border-color: #D4AF37;
        }

        .text-brand-blue {
          color: #0088CC;
        }

        .glass-panel {
          background: rgba(18, 21, 28, 0.7);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .gold-gradient {
          background: linear-gradient(135deg, #E6C875 0%, #D4AF37 50%, #AA8C2C 100%);
        }

        .gold-gradient-text {
          background: linear-gradient(135deg, #E6C875 0%, #D4AF37 50%, #AA8C2C 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        
        .hover-gold:hover {
          color: #D4AF37;
          transition: all 0.3s ease;
        }

        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}} />

      <div className="min-h-screen bg-luxury-dark text-gray-200 font-sans selection:bg-[#D4AF37] selection:text-black pb-24 lg:pb-0">
        
        {/* Navigation / Breadcrumbs overlay */}
        <div className="absolute top-0 left-0 right-0 z-50 p-6 flex justify-between items-center bg-gradient-to-b from-black/80 to-transparent">
          <div className="flex items-center space-x-2 text-sm text-gray-300 font-medium tracking-wide">
            <span className="hover:text-white cursor-pointer transition-colors">Главная</span>
            <ChevronRight size={14} className="text-gray-500" />
            <span className="hover:text-white cursor-pointer transition-colors">Новостройки</span>
            <ChevronRight size={14} className="text-gray-500" />
            <span className="text-gold">ЖК «Тёплые края»</span>
          </div>
          <div className="flex items-center space-x-4">
            <button className="p-2 rounded-full glass-panel hover:bg-white/10 transition-colors text-white">
              <Share2 size={18} />
            </button>
            <button className="p-2 rounded-full glass-panel hover:bg-white/10 transition-colors text-white">
              <Heart size={18} />
            </button>
          </div>
        </div>

        {/* Hero Section */}
        <div className="relative h-[60vh] lg:h-[75vh] w-full bg-[#1A1D24] overflow-hidden">
          <img 
            src="/__mockup/images/luxury-ext.png" 
            alt="ЖК Тёплые края" 
            className="w-full h-full object-cover opacity-60 object-center"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-luxury-dark via-luxury-dark/40 to-transparent" />
          
          <div className="absolute bottom-0 left-0 w-full p-6 lg:p-12 lg:px-24">
            <div className="max-w-7xl mx-auto flex flex-col lg:flex-row lg:items-end justify-between gap-6">
              <div className="max-w-2xl">
                <div className="flex flex-wrap items-center gap-3 mb-4">
                  <span className="px-3 py-1 text-xs font-semibold uppercase tracking-wider text-black bg-gold rounded-sm">
                    Премиум
                  </span>
                  <span className="px-3 py-1 text-xs font-medium text-gray-300 glass-panel rounded-sm flex items-center gap-1.5">
                    <MapPin size={12} className="text-gold" />
                    Краснодар, р-н Западный
                  </span>
                  <span className="px-3 py-1 text-xs font-medium text-gray-300 glass-panel rounded-sm">
                    Сдача 4 кв. 2025
                  </span>
                </div>
                
                <h1 className="text-4xl lg:text-6xl font-serif text-white leading-tight mb-4">
                  Студия, 20.03 м² <br className="hidden lg:block"/>
                  <span className="text-gray-400 text-3xl lg:text-5xl">в ЖК «Тёплые края»</span>
                </h1>
              </div>
            </div>
          </div>
        </div>

        {/* Gallery Strip */}
        <div className="px-6 lg:px-24 -mt-6 relative z-20">
          <div className="max-w-7xl mx-auto flex gap-3 overflow-x-auto hide-scrollbar snap-x pb-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="relative flex-none w-32 h-24 lg:w-48 lg:h-32 rounded-lg overflow-hidden snap-center cursor-pointer group border border-white/5 hover:border-gold/50 transition-colors">
                <div className="absolute inset-0 bg-gradient-to-tr from-[#12151C] to-[#2A2F3D] mix-blend-overlay"></div>
                <img 
                  src={i === 1 ? "/__mockup/images/luxury-int.png" : "/__mockup/images/luxury-ext.png"} 
                  alt="Interior" 
                  className={`w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 ${i > 1 ? 'filter grayscale contrast-125 opacity-40' : ''}`}
                />
                {i === 5 && (
                  <div className="absolute inset-0 bg-black/60 flex items-center justify-center backdrop-blur-sm">
                    <span className="text-white font-medium flex items-center gap-2">
                      <Maximize2 size={16} /> +12
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content Layout */}
        <div className="max-w-7xl mx-auto px-6 lg:px-24 py-12 lg:py-20 flex flex-col lg:flex-row gap-12">
          
          {/* Left Column - Details */}
          <div className="w-full lg:w-2/3 space-y-16">
            
            {/* Characteristics Grid */}
            <section>
              <h2 className="text-2xl font-serif text-white mb-8 flex items-center gap-4">
                <span className="w-8 h-px bg-gold"></span>
                О квартире
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-luxury-panel p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                  <Ruler className="text-gold mb-3" size={24} strokeWidth={1.5} />
                  <div className="text-sm text-gray-500 mb-1">Площадь</div>
                  <div className="text-lg font-medium text-white">20.03 м²</div>
                </div>
                <div className="bg-luxury-panel p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                  <DoorOpen className="text-gold mb-3" size={24} strokeWidth={1.5} />
                  <div className="text-sm text-gray-500 mb-1">Комнат</div>
                  <div className="text-lg font-medium text-white">Студия</div>
                </div>
                <div className="bg-luxury-panel p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                  <ArrowUpToLine className="text-gold mb-3" size={24} strokeWidth={1.5} />
                  <div className="text-sm text-gray-500 mb-1">Этаж</div>
                  <div className="text-lg font-medium text-white">4 из 18</div>
                </div>
                <div className="bg-luxury-panel p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                  <Hammer className="text-gold mb-3" size={24} strokeWidth={1.5} />
                  <div className="text-sm text-gray-500 mb-1">Отделка</div>
                  <div className="text-lg font-medium text-white">Чистовая</div>
                </div>
                <div className="bg-luxury-panel p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                  <Calendar className="text-gold mb-3" size={24} strokeWidth={1.5} />
                  <div className="text-sm text-gray-500 mb-1">Срок сдачи</div>
                  <div className="text-lg font-medium text-white">4 кв. 2025</div>
                </div>
                <div className="bg-luxury-panel p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                  <Building className="text-gold mb-3" size={24} strokeWidth={1.5} />
                  <div className="text-sm text-gray-500 mb-1">Тип дома</div>
                  <div className="text-lg font-medium text-white">Монолит</div>
                </div>
              </div>
            </section>

            {/* Description */}
            <section>
              <h2 className="text-2xl font-serif text-white mb-6 flex items-center gap-4">
                <span className="w-8 h-px bg-gold"></span>
                Описание
              </h2>
              <div className="prose prose-invert max-w-none text-gray-400 font-light leading-relaxed">
                <p>
                  Идеальная студия для инвестиций или первого жилья в одном из самых востребованных комплексов Краснодара. 
                  Продуманная эргономика пространства позволяет комфортно разместить зону кухни, зону отдыха и вместительные системы хранения.
                </p>
                <p className="mt-4">
                  Высокие потолки (2.9м) и панорамное остекление наполняют квартиру естественным светом. 
                  Чистовая отделка выполнена с использованием премиальных материалов: инженерная доска, 
                  керамогранит в мокрых зонах, установлена качественная сантехника.
                </p>
              </div>
            </section>

            {/* Complex Info Block */}
            <section>
              <h2 className="text-2xl font-serif text-white mb-6 flex items-center gap-4">
                <span className="w-8 h-px bg-gold"></span>
                О жилом комплексе
              </h2>
              <div className="bg-luxury-panel border border-white/5 rounded-2xl overflow-hidden">
                <div className="h-48 bg-[#1A1D24] relative border-b border-white/5">
                  <div className="absolute inset-0 opacity-20 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4=')]"></div>
                  <div className="absolute inset-0 flex items-center justify-center flex-col">
                    <MapPin className="text-gold mb-2" size={32} />
                    <span className="text-sm font-medium text-gray-300">Открыть на карте</span>
                  </div>
                </div>
                <div className="p-8">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-xl font-serif text-white mb-1">ЖК «Тёплые края»</h3>
                      <p className="text-gray-400 text-sm">Застройщик: Dogma (Надежность 5/5)</p>
                    </div>
                    <div className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center">
                      <Star className="text-gold" size={20} />
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-2 mb-6">
                    {['Закрытая территория', 'Двор без машин', 'Подземный паркинг', 'Собственный парк', 'Школа на территории', 'Торговая галерея'].map((tag) => (
                      <span key={tag} className="px-3 py-1.5 text-xs text-gray-400 bg-white/5 rounded-full border border-white/5">
                        {tag}
                      </span>
                    ))}
                  </div>

                  <button className="text-gold text-sm font-medium flex items-center gap-2 hover:text-white transition-colors">
                    Подробнее о ЖК <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            </section>

            {/* Cashback Calculator visual */}
            <section className="bg-gradient-to-br from-[#12151C] to-[#1A1D24] p-8 rounded-2xl border border-white/5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-gold/5 rounded-full blur-3xl -mr-20 -mt-20"></div>
              
              <div className="flex items-center gap-3 mb-6 relative z-10">
                <Calculator className="text-brand-blue" size={24} />
                <h2 className="text-xl font-serif text-white">Калькулятор кэшбека</h2>
              </div>
              
              <div className="space-y-8 relative z-10">
                <div>
                  <div className="flex justify-between text-sm mb-3">
                    <span className="text-gray-400">Сумма покупки</span>
                    <span className="text-white font-medium">3 870 000 ₽</span>
                  </div>
                  <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-gray-500 w-1/3 rounded-full"></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-3">
                    <span className="text-gray-400">Процент кэшбека</span>
                    <span className="text-gold font-medium">3.5% (InBack Premium)</span>
                  </div>
                  <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-gold w-3/4 rounded-full shadow-[0_0_10px_rgba(212,175,55,0.5)]"></div>
                  </div>
                </div>

                <div className="p-6 bg-black/40 rounded-xl border border-gold/20 flex items-center justify-between">
                  <div>
                    <div className="text-gray-400 text-sm mb-1">Вы получите назад:</div>
                    <div className="gold-gradient-text text-3xl font-serif font-bold">135 450 ₽</div>
                  </div>
                  <div className="hidden sm:flex h-12 w-12 rounded-full bg-gold/10 items-center justify-center">
                    <ShieldCheck className="text-gold" size={24} />
                  </div>
                </div>
              </div>
            </section>
            
          </div>

          {/* Right Column - Sticky CTA */}
          <div className="w-full lg:w-1/3 relative">
            <div className="sticky top-24 space-y-6">
              
              {/* Main Price Card */}
              <div className="bg-luxury-panel rounded-2xl border border-white/5 p-6 lg:p-8 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-gold/10 rounded-full blur-2xl -mr-10 -mt-10"></div>
                
                <div className="mb-2 relative z-10">
                  <span className="text-gray-400 text-sm">Стоимость объекта</span>
                </div>
                <div className="text-4xl font-serif font-medium text-white mb-2 relative z-10">
                  3 870 000 ₽
                </div>
                <div className="text-gray-500 text-sm mb-8 relative z-10">
                  ~ 193 000 ₽/м²
                </div>

                {/* Cashback Highlight */}
                <div className="mb-8 p-4 rounded-xl bg-gradient-to-r from-gold/10 to-transparent border-l-2 border-gold">
                  <div className="text-xs text-gold/80 font-medium tracking-wide uppercase mb-1">InBack Premium</div>
                  <div className="text-lg text-white font-medium">Кэшбек <span className="text-gold">135 450 ₽</span></div>
                  <div className="text-sm text-gray-400 mt-1">При покупке через нашу платформу</div>
                </div>

                <div className="space-y-4 relative z-10">
                  <button className="w-full py-4 rounded-lg text-black font-semibold text-sm tracking-wide uppercase transition-all duration-300 gold-gradient hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] hover:-translate-y-0.5">
                    Получить кэшбек
                  </button>
                  <button className="w-full py-4 rounded-lg text-white font-medium text-sm transition-all duration-300 bg-white/5 border border-white/10 hover:bg-white/10">
                    Записаться на просмотр
                  </button>
                </div>
                
                <div className="mt-6 pt-6 border-t border-white/5 text-center relative z-10">
                  <button className="text-sm text-brand-blue hover:text-white transition-colors flex items-center justify-center gap-2 w-full">
                    <Heart size={16} /> Добавить в сравнение
                  </button>
                </div>
              </div>

              {/* Manager Card */}
              <div className="bg-luxury-panel rounded-2xl border border-white/5 p-6 flex items-start gap-4">
                <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-gray-800 to-gray-600 flex-shrink-0 border border-white/10 overflow-hidden">
                  <div className="w-full h-full bg-gray-700 flex items-center justify-center text-gray-400 font-serif">A</div>
                </div>
                <div>
                  <div className="text-xs text-gold mb-1 font-medium tracking-wide uppercase">Ваш эксперт</div>
                  <div className="text-white font-medium mb-1">Александр</div>
                  <div className="text-sm text-gray-400 mb-4">Ответит на вопросы и организует показ</div>
                  <div className="flex gap-2">
                    <button className="p-2.5 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors text-white flex-1 flex justify-center">
                      <Phone size={18} />
                    </button>
                    <button className="p-2.5 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors text-white flex-1 flex justify-center">
                      <MessageCircle size={18} />
                    </button>
                  </div>
                </div>
              </div>

            </div>
          </div>

        </div>

        {/* Similar Properties */}
        <div className="max-w-7xl mx-auto px-6 lg:px-24 pb-24 lg:pb-32">
          <div className="flex items-end justify-between mb-8">
            <h2 className="text-2xl font-serif text-white flex items-center gap-4">
              <span className="w-8 h-px bg-gold"></span>
              Похожие предложения
            </h2>
            <button className="text-sm text-gray-400 hover:text-gold transition-colors hidden sm:block">
              Смотреть все
            </button>
          </div>
          
          <div className="flex gap-6 overflow-x-auto hide-scrollbar snap-x pb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex-none w-72 lg:w-1/4 snap-start group cursor-pointer">
                <div className="bg-luxury-panel rounded-2xl border border-white/5 overflow-hidden transition-all duration-300 hover:border-gold/30 hover:-translate-y-1">
                  <div className="h-48 bg-[#1A1D24] relative overflow-hidden">
                    <img 
                      src={i % 2 === 0 ? "/__mockup/images/luxury-int.png" : "/__mockup/images/luxury-ext.png"} 
                      alt="Property" 
                      className="w-full h-full object-cover opacity-60 group-hover:opacity-80 group-hover:scale-105 transition-all duration-500"
                    />
                    <div className="absolute top-3 left-3 px-2 py-1 bg-black/60 backdrop-blur-md rounded text-xs text-white border border-white/10">
                      Студия
                    </div>
                  </div>
                  <div className="p-5">
                    <div className="text-xl font-serif text-white mb-1">{3800000 + (i * 150000)} ₽</div>
                    <div className="text-sm text-gray-400 mb-4">ЖК «Оазис» • 21 м²</div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-gold">Кэшбек ~{(130000 + i * 5000).toLocaleString()} ₽</span>
                      <span className="text-gray-500">Сдача 2026</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Mobile Sticky Footer */}
        <div className="fixed bottom-0 left-0 right-0 glass-panel border-t border-white/10 p-4 lg:hidden z-50 flex items-center justify-between">
          <div>
            <div className="text-xl font-serif text-white font-medium">3 870 000 ₽</div>
            <div className="text-xs text-gold">Кэшбек 135 450 ₽</div>
          </div>
          <button className="px-6 py-3 rounded-lg text-black font-semibold text-sm tracking-wide uppercase gold-gradient">
            Получить
          </button>
        </div>

      </div>
    </>
  );
}
