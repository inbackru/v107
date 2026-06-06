# Overview

InBack/Clickback is a Flask-based real estate platform specializing in cashback services for new construction properties (Krasnodar region, expanding). Key features: cashback incentives, property search with maps, property comparison, manager dashboard, CRM, MLM affiliate program.

# User Preferences

- Communication: simple, everyday Russian.
- Brand color: `#0088CC` (rgb(0 136 204)). No purple/violet/fuchsia in UI.
- Mobile-first responsive design.

# Stack

- **Backend**: Flask + SQLAlchemy + PostgreSQL, Flask-Login. Blueprints. APScheduler for jobs.
- **Frontend**: Jinja2 SSR + TailwindCSS (CDN) + vanilla JS. Yandex Maps, Chart.js.
- **Auth**: Flask-Login. User types: User / Manager / Partner / Admin. Partners use `p_` session prefix. Phone+SMS verification (Telegram Gateway primary, RED SMS fallback). Email/phone changes require verification through `EmailChangeRequest` / `PhoneChangeRequest` models. Social OAuth (Google, VK, Mail.ru, Telegram) via `social_auth.py`.
- **Integrations**: SendGrid, OpenAI, Telegram Bot, Yandex Maps, DaData.ru, RED SMS, Telegram Gateway, Google Analytics, LaunchDarkly, Chaport, reCAPTCHA, ipwho.is.
- **Scraping/PDF/Images**: selenium, playwright, beautifulsoup4, undetected-chromedriver, weasyprint, reportlab, Pillow.

# Notes for the Agent

- Cache buster strings used on key JS/HTML files — bump when shipping JS/CSS changes that need fresh client load.
- `/api/map-properties/aggregated` has in-memory cache (60s TTL) for unfiltered city requests.
- Fullscreen map modal lives inside `templates/properties.html` (id `#fullscreenMapModal`). Filter modal is `#mapAdvancedFiltersModal`. Chip styles are applied inline (Tailwind/custom CSS conflicts caused issues).
- Manager notification preferences: 9 columns on Manager model; `send_manager_notification()` in `email_service.py` honors them.
- `PromoBanner` model + `/admin/banners` CRUD; active banner injected via `inject_promo_banner` context processor.
- `PriceHistory` model + monthly APScheduler snapshot job; charts on complex/property detail pages.
- `ComplexReview` model with moderation at `/admin/reviews`.
- CSRF error handler in `security_config.py` distinguishes AJAX vs form POST and returns JSON or redirect accordingly.
- Map filter pipeline (`/krasnodar/novostrojki` fullscreen): unified through `window.updateMapWithFilters` (debounced, in `static/js/properties_mini_map.js`). Canonical UI-side wrappers `window.applyMapAdvancedFilters`, `window.resetMapAdvancedFilters`, `window.fetchAndUpdateFilteredCount` live in `templates/properties.html` (bottom of file). **Do not assign these `window.*` names anywhere else** — shadowing silently breaks live preview. Run `bash scripts/check_no_shadow_map_filters.sh` to verify.

# External Services (Env Vars)

- `SESSION_SECRET`, `DATABASE_URL`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_GATEWAY_TOKEN`
- `SENDGRID_API_KEY`, `OPENAI_API_KEY`
- `YANDEX_MAPS_API_KEY`, `DADATA_API_KEY`, `DADATA_SECRET_KEY`
- OAuth (optional): `GOOGLE_OAUTH_CLIENT_ID/SECRET`, `VK_CLIENT_ID/SECRET`, `MAILRU_CLIENT_ID/SECRET`, `TELEGRAM_BOT_USERNAME`
