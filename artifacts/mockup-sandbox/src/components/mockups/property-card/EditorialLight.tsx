import React from "react";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "../../ui/breadcrumb";
import { Button } from "../../ui/button";
import { Card, CardContent } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "../../ui/avatar";
import { 
  Heart, 
  Share2, 
  MapPin, 
  ChevronRight, 
  Star, 
  Building2, 
  ShieldCheck, 
  Maximize2,
  Image as ImageIcon,
  CheckCircle2,
  Info
} from "lucide-react";

export function EditorialLight() {
  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-[#0088CC]/20" style={{ fontFamily: '"Inter", sans-serif' }}>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      
      {/* Top Navigation Bar / Breadcrumbs */}
      <div className="border-b border-slate-100">
        <div className="container mx-auto px-4 lg:px-8 py-4 flex items-center justify-between">
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="#" className="text-slate-500 hover:text-[#0088CC]">Краснодар</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbLink href="#" className="text-slate-500 hover:text-[#0088CC]">Новостройки</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbLink href="#" className="text-slate-500 hover:text-[#0088CC]">ЖК «Тёплые края»</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <span className="text-slate-900 font-medium">Студия, 20.03 м²</span>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <div className="flex items-center gap-4 text-sm text-slate-500">
            <button className="flex items-center gap-1.5 hover:text-[#0088CC] transition-colors">
              <Share2 className="w-4 h-4" />
              <span className="hidden sm:inline">Поделиться</span>
            </button>
            <button className="flex items-center gap-1.5 hover:text-[#0088CC] transition-colors">
              <Heart className="w-4 h-4" />
              <span className="hidden sm:inline">В избранное</span>
            </button>
          </div>
        </div>
      </div>

      <main className="container mx-auto px-4 lg:px-8 py-6 pb-32">
        {/* Hero Section */}
        <div className="flex flex-col lg:flex-row gap-6 mb-4">
          <div className="w-full lg:w-2/3 flex flex-col gap-2 relative group cursor-pointer rounded-2xl overflow-hidden">
            <div className="aspect-[16/9] w-full relative">
              <img 
                src="/__mockup/images/studio-interior.png" 
                alt="Studio interior" 
                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
              />
              {/* Overlays */}
              <div className="absolute top-4 left-4 flex gap-2">
                <Badge className="bg-[#0088CC] text-white hover:bg-[#0088CC]/90 border-none font-medium px-3 py-1 text-sm shadow-sm">
                  Кэшбек 3.5%
                </Badge>
                <Badge variant="secondary" className="bg-white/90 backdrop-blur-md text-slate-800 border-none font-medium px-3 py-1 text-sm shadow-sm">
                  Новостройка
                </Badge>
              </div>
              <div className="absolute bottom-4 right-4 flex gap-2">
                <div className="bg-black/60 backdrop-blur-md text-white text-sm font-medium px-3 py-1.5 rounded-lg flex items-center gap-2">
                  <ImageIcon className="w-4 h-4" />
                  1 / 12
                </div>
                <button className="bg-black/60 backdrop-blur-md text-white p-1.5 rounded-lg hover:bg-black/80 transition-colors">
                  <Maximize2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
          
          <div className="w-full lg:w-1/3 flex flex-col justify-between hidden lg:flex rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
            <div>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h1 className="text-3xl font-bold tracking-tight text-slate-900 mb-1">3 870 000 ₽</h1>
                  <p className="text-slate-500">193 000 ₽/м²</p>
                </div>
                <button className="text-slate-400 hover:text-red-500 transition-colors">
                  <Heart className="w-6 h-6" />
                </button>
              </div>
              
              <div className="bg-blue-50/50 rounded-xl p-4 mb-6 border border-blue-100">
                <div className="flex items-start gap-3">
                  <div className="bg-[#0088CC] rounded-full p-1.5 mt-0.5">
                    <CheckCircle2 className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 mb-1">Ваша выгода до 135 450 ₽</h3>
                    <p className="text-sm text-slate-600 leading-relaxed">Вернем кэшбек на карту после оформления сделки. Без скрытых условий.</p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <Button className="w-full h-12 bg-[#0088CC] hover:bg-[#0077b3] text-white font-medium text-base rounded-xl transition-all shadow-sm shadow-blue-200">
                  Получить кэшбек
                </Button>
                <Button variant="outline" className="w-full h-12 border-slate-200 text-slate-700 font-medium text-base rounded-xl hover:bg-slate-50 transition-all">
                  Связаться с менеджером
                </Button>
              </div>
            </div>
            
            <div className="mt-8 pt-6 border-t border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10 border border-slate-100">
                  <AvatarImage src="https://i.pravatar.cc/150?u=a042581f4e29026024d" />
                  <AvatarFallback>ЕМ</AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-medium text-slate-900">Екатерина М.</p>
                  <p className="text-xs text-slate-500">Эксперт по новостройкам</p>
                </div>
              </div>
              <Button variant="ghost" size="sm" className="rounded-lg text-[#0088CC] hover:bg-blue-50 hover:text-[#0077b3]">
                Показать номер
              </Button>
            </div>
          </div>
        </div>

        {/* Thumbnail Gallery */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2 scrollbar-hide">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="w-32 h-24 flex-shrink-0 rounded-xl overflow-hidden cursor-pointer group relative">
              <img 
                src="/__mockup/images/studio-interior.png" 
                alt="Thumbnail" 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" 
              />
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
            </div>
          ))}
          <button className="w-32 h-24 flex-shrink-0 rounded-xl bg-slate-100 flex flex-col items-center justify-center text-slate-600 hover:bg-slate-200 transition-colors group">
            <ImageIcon className="w-5 h-5 mb-1 group-hover:text-[#0088CC] transition-colors" />
            <span className="text-sm font-medium">Ещё 8 фото</span>
          </button>
        </div>

        <div className="flex flex-col lg:flex-row gap-10">
          {/* Main Content Column */}
          <div className="w-full lg:w-2/3">
            
            {/* Title & Pills */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-slate-900 mb-4 tracking-tight">Студия, 20.03 м² в ЖК «Тёплые края»</h2>
              <div className="flex flex-wrap gap-2">
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-slate-50 text-slate-700 text-sm border border-slate-100">
                  Студия
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-slate-50 text-slate-700 text-sm border border-slate-100">
                  20.03 м²
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-slate-50 text-slate-700 text-sm border border-slate-100">
                  4 этаж из 18
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-slate-50 text-slate-700 text-sm border border-slate-100">
                  Чистовая отделка
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-slate-50 text-slate-700 text-sm border border-slate-100">
                  Сдача Q4 2025
                </span>
              </div>
            </div>

            {/* Description */}
            <div className="prose prose-slate max-w-none mb-10">
              <p className="text-slate-600 leading-relaxed">
                Светлая и уютная студия в новом современном жилом комплексе комфорт-класса. 
                Отличный вариант как для собственного проживания, так и для инвестиций. 
                Выполнена качественная чистовая отделка от застройщика — можно заезжать сразу после получения ключей. 
                Окна выходят на солнечную сторону, открывая прекрасный вид на благоустроенный двор без машин.
              </p>
              <button className="text-[#0088CC] font-medium hover:underline mt-2 flex items-center gap-1">
                Читать полностью <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            {/* Characteristics Table */}
            <h3 className="text-xl font-bold mb-6 text-slate-900 tracking-tight">Характеристики</h3>
            <div className="bg-white border border-slate-100 rounded-2xl overflow-hidden mb-12 shadow-sm">
              <div className="grid grid-cols-1 sm:grid-cols-2">
                {[
                  { label: "Общая площадь", value: "20.03 м²" },
                  { label: "Жилая площадь", value: "12.5 м²" },
                  { label: "Площадь кухни", value: "—" },
                  { label: "Высота потолков", value: "2.7 м" },
                  { label: "Этаж", value: "4 из 18" },
                  { label: "Тип дома", value: "Монолитно-кирпичный" },
                  { label: "Отделка", value: "Чистовая" },
                  { label: "Санузел", value: "1 совмещенный" },
                  { label: "Балкон/Лоджия", value: "Лоджия" },
                  { label: "Окна", value: "Во двор" },
                ].map((item, index) => (
                  <div key={index} className={`flex justify-between p-4 ${index % 4 === 0 || index % 4 === 1 ? 'bg-slate-50/50' : 'bg-white'} ${index % 2 === 0 ? 'sm:border-r border-slate-100' : ''}`}>
                    <span className="text-slate-500">{item.label}</span>
                    <span className="font-medium text-slate-900">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Mortgage Calculator */}
            <h3 className="text-xl font-bold mb-6 text-slate-900 tracking-tight">Ипотека</h3>
            <div className="bg-slate-50 rounded-2xl p-6 mb-12 border border-slate-100">
              <div className="flex items-center gap-2 mb-6">
                <span className="text-3xl font-bold text-slate-900">от 14 500 ₽/мес</span>
                <Info className="w-5 h-5 text-slate-400 cursor-help" />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group cursor-pointer hover:border-[#0088CC] transition-colors">
                  <div className="absolute top-0 right-0 w-16 h-16 bg-blue-50 rounded-bl-full -mr-8 -mt-8 group-hover:scale-110 transition-transform" />
                  <div className="text-sm text-slate-500 mb-1">Семейная</div>
                  <div className="font-bold text-lg text-slate-900 mb-2">3.5%</div>
                  <div className="text-[#0088CC] font-medium">14 500 ₽/мес</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm cursor-pointer hover:border-[#0088CC] transition-colors">
                  <div className="text-sm text-slate-500 mb-1">IT Ипотека</div>
                  <div className="font-bold text-lg text-slate-900 mb-2">3.5%</div>
                  <div className="text-[#0088CC] font-medium">14 500 ₽/мес</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm cursor-pointer hover:border-[#0088CC] transition-colors">
                  <div className="text-sm text-slate-500 mb-1">Стандартная</div>
                  <div className="font-bold text-lg text-slate-900 mb-2">8%</div>
                  <div className="text-slate-900 font-medium">25 300 ₽/мес</div>
                </div>
              </div>
              <Button variant="outline" className="w-full mt-6 bg-white border-slate-200 text-slate-700 hover:bg-slate-50">
                Рассчитать подробнее
              </Button>
            </div>

            {/* Building Info */}
            <h3 className="text-xl font-bold mb-6 text-slate-900 tracking-tight">О жилом комплексе</h3>
            <div className="border border-slate-100 rounded-2xl overflow-hidden mb-12 shadow-sm">
              <div className="aspect-[21/9] w-full relative bg-slate-100">
                <img 
                  src="/__mockup/images/building-exterior.png" 
                  alt="Building exterior" 
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-4 left-4 bg-white/90 backdrop-blur px-4 py-2 rounded-xl flex items-center gap-3 shadow-sm">
                  <div className="w-8 h-8 bg-slate-200 rounded-md flex items-center justify-center font-bold text-slate-400 text-xs">ЛОГО</div>
                  <div>
                    <div className="font-bold text-slate-900 leading-none mb-1">ЖК «Тёплые края»</div>
                    <div className="text-xs text-slate-500 leading-none">Застройщик: ИНСИТИ</div>
                  </div>
                </div>
              </div>
              <div className="p-6 bg-white">
                <div className="flex items-start gap-2 mb-6 text-slate-600">
                  <MapPin className="w-5 h-5 text-slate-400 flex-shrink-0 mt-0.5" />
                  <p>Краснодар, микрорайон Энка, улица Героя Пешкова, 14</p>
                </div>
                <div className="flex flex-wrap gap-2 mb-6">
                  <span className="bg-slate-50 px-3 py-1.5 rounded-lg text-sm text-slate-700 flex items-center gap-1.5 border border-slate-100">
                    <Building2 className="w-4 h-4 text-slate-400" /> Комфорт-класс
                  </span>
                  <span className="bg-slate-50 px-3 py-1.5 rounded-lg text-sm text-slate-700 flex items-center gap-1.5 border border-slate-100">
                    <ShieldCheck className="w-4 h-4 text-slate-400" /> Двор без машин
                  </span>
                  <span className="bg-slate-50 px-3 py-1.5 rounded-lg text-sm text-slate-700 border border-slate-100">
                    Подземный паркинг
                  </span>
                  <span className="bg-slate-50 px-3 py-1.5 rounded-lg text-sm text-slate-700 border border-slate-100">
                    Школа во дворе
                  </span>
                </div>
                
                {/* Map Placeholder */}
                <div className="w-full h-48 bg-blue-50/50 rounded-xl border border-blue-100 flex items-center justify-center relative overflow-hidden group cursor-pointer">
                  <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+PHBhdGggZD0iTTAgMGgyMHYyMEgwem0xMCAxMGgyMHYyMEgxMHoiIGZpbGw9IiNlMmU4ZjAiIGZpbGwtb3BhY2l0eT0iLjQiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==')] opacity-50" />
                  <div className="relative flex flex-col items-center group-hover:scale-110 transition-transform duration-300">
                    <MapPin className="w-8 h-8 text-[#0088CC] drop-shadow-md" />
                    <span className="mt-2 bg-white px-3 py-1 rounded-full text-sm font-medium text-slate-700 shadow-sm border border-slate-100">
                      Смотреть на карте
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Reviews */}
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-slate-900 tracking-tight">Отзывы о застройщике</h3>
              <div className="flex items-center gap-1 text-slate-900 font-bold">
                <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                4.8
                <span className="text-slate-400 font-normal ml-1">(124)</span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
              {[
                { name: "Александр В.", date: "12 мая 2024", text: "Надежный застройщик, сдают вовремя. Качество отделки приемлемое, дворы отличные." },
                { name: "Мария С.", date: "3 апр 2024", text: "Купили здесь квартиру, менеджеры приятные, помогли с ипотекой. Ждем ключи." },
                { name: "Иван П.", date: "28 мар 2024", text: "Хорошее расположение, цены адекватные для комфорт-класса. Инфраструктура развивается." },
              ].map((review, i) => (
                <div key={i} className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                  <div className="flex items-center gap-3 mb-3">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={`https://i.pravatar.cc/150?u=${i}`} />
                      <AvatarFallback>{review.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="font-medium text-slate-900 text-sm">{review.name}</div>
                      <div className="text-xs text-slate-500">{review.date}</div>
                    </div>
                    <div className="ml-auto flex gap-0.5">
                      {[1,2,3,4,5].map(star => <Star key={star} className="w-3.5 h-3.5 fill-yellow-400 text-yellow-400" />)}
                    </div>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">{review.text}</p>
                </div>
              ))}
            </div>

          </div>

          {/* Sticky Sidebar */}
          <div className="w-full lg:w-1/3">
            <div className="sticky top-6">
              {/* Mobile fallback price block (shown inline on mobile, hidden on lg as we have the hero block, wait we want sidebar on lg as well if scrolling) */}
              <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm mb-6 block lg:hidden">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900 mb-1">3 870 000 ₽</h1>
                    <p className="text-slate-500">193 000 ₽/м²</p>
                  </div>
                </div>
                
                <div className="bg-blue-50/50 rounded-xl p-4 mb-6 border border-blue-100">
                  <div className="flex items-start gap-3">
                    <div className="bg-[#0088CC] rounded-full p-1.5 mt-0.5">
                      <CheckCircle2 className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 mb-1">Ваша выгода до 135 450 ₽</h3>
                      <p className="text-sm text-slate-600">Вернем кэшбек на карту после оформления сделки.</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <Button className="w-full h-12 bg-[#0088CC] hover:bg-[#0077b3] text-white font-medium text-base rounded-xl">
                    Получить кэшбек
                  </Button>
                  <Button variant="outline" className="w-full h-12 border-slate-200 text-slate-700 font-medium text-base rounded-xl">
                    Связаться с менеджером
                  </Button>
                </div>
              </div>

              {/* Sidebar Content (visible on lg, duplicates hero CTA to stay visible on scroll) */}
              <div className="hidden lg:block rounded-2xl border border-slate-100 bg-white p-6 shadow-sm mb-6">
                <div className="mb-4">
                  <h2 className="text-2xl font-bold tracking-tight text-slate-900 mb-1">3 870 000 ₽</h2>
                  <p className="text-slate-500 text-sm">193 000 ₽/м²</p>
                </div>
                
                <div className="bg-[#0088CC] text-white rounded-xl p-4 mb-6 shadow-md shadow-blue-200">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-white mt-0.5 opacity-90" />
                    <div>
                      <h3 className="font-semibold mb-1">Ваша выгода до 135 450 ₽</h3>
                      <p className="text-sm text-white/80 leading-snug">Гарантированный кэшбек при покупке через InBack</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <Button className="w-full h-12 bg-[#0088CC] hover:bg-[#0077b3] text-white font-medium text-base rounded-xl shadow-sm">
                    Получить кэшбек
                  </Button>
                  <Button variant="outline" className="w-full h-12 border-slate-200 text-slate-700 font-medium text-base rounded-xl hover:bg-slate-50">
                    Связаться с менеджером
                  </Button>
                </div>

                <div className="mt-6 pt-6 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10 border border-slate-100">
                      <AvatarImage src="https://i.pravatar.cc/150?u=a042581f4e29026024d" />
                      <AvatarFallback>ЕМ</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="text-sm font-medium text-slate-900">Екатерина М.</p>
                      <p className="text-xs text-slate-500">Эксперт по новостройкам</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Promo Banner */}
              <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-6 text-white relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-2xl -mr-10 -mt-10 group-hover:scale-150 transition-transform duration-700" />
                <h3 className="font-bold text-lg mb-2">Бесплатный подбор</h3>
                <p className="text-slate-300 text-sm mb-4">Найдем лучшую квартиру под ваш бюджет и оформим ипотеку.</p>
                <Button className="w-full bg-white text-slate-900 hover:bg-slate-50 rounded-xl h-10">
                  Оставить заявку
                </Button>
              </div>

            </div>
          </div>
        </div>

        {/* Similar Apartments */}
        <div className="mt-16 pt-12 border-t border-slate-100">
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight mb-6">Похожие квартиры</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="group cursor-pointer">
                <div className="aspect-[4/3] rounded-2xl overflow-hidden mb-3 relative bg-slate-100">
                  <img 
                    src="/__mockup/images/studio-interior.png" 
                    alt="Similar" 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-2 left-2 bg-white/90 backdrop-blur text-xs font-medium px-2 py-1 rounded-md text-slate-800">
                    Студия
                  </div>
                  <button className="absolute top-2 right-2 p-1.5 text-white/80 hover:text-white bg-black/20 hover:bg-black/40 rounded-full backdrop-blur-md transition-colors">
                    <Heart className="w-4 h-4" />
                  </button>
                </div>
                <div className="font-bold text-lg text-slate-900 mb-1">{(3.5 + i * 0.1).toFixed(1)} млн ₽</div>
                <div className="text-sm text-slate-600 mb-1">Студия, 21 м² · 5/18 этаж</div>
                <div className="text-xs text-slate-500">ЖК «Тёплые края»</div>
                <div className="mt-2 inline-block text-xs font-medium text-[#0088CC] bg-blue-50 px-2 py-1 rounded-md">
                  Кэшбек до 120 тыс. ₽
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Mobile Sticky Bottom Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 p-4 pb-safe lg:hidden z-50 shadow-[0_-4px_20px_-10px_rgba(0,0,0,0.1)]">
        <div className="flex items-center justify-between gap-4 container mx-auto">
          <div>
            <div className="font-bold text-lg text-slate-900 leading-tight">3 870 000 ₽</div>
            <div className="text-xs text-[#0088CC] font-medium">Кэшбек 135 450 ₽</div>
          </div>
          <Button className="bg-[#0088CC] hover:bg-[#0077b3] text-white rounded-xl h-12 px-6 shadow-sm flex-1 max-w-[200px]">
            Получить
          </Button>
        </div>
      </div>

    </div>
  );
}
