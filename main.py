import asyncio
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, filters
from telegram.error import BadRequest, NetworkError
import aiosqlite
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from config import BOT_TOKEN, DB_PATH, ITEMS_PER_PAGE, api_id, api_hash, phone_number

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Pyrogram клиент
client = Client("seo_seduction_session", api_id=api_id, api_hash=api_hash, phone_number=phone_number)

# Блокировка для базы
db_lock = asyncio.Lock()

# Тексты и кнопки
INITIAL_WELCOME_TEXT = {
    "ru": (
        "Привет! Я бот для SEO и новостей Telegram.\n"
        "Что я умею:\n"
        "- SEO за сегодня: последние посты\n"
        "- SEO за 3 месяца: посты за 90 дней\n"
        "- Суммаризация: краткий обзор за 3 месяца\n"
        "- Прогноз трафика: расчёт трафика и ссылок\n"
        "- Глоссарий: термины SEO\n"
        "- Перезагрузить: обновить данные\n"
        "Выбери язык ниже!"
    ),
    "ua": (
        "Привіт! Я бот для SEO та новин Telegram.\n"
        "Що я вмію:\n"
        "- SEO за сьогодні: останні пости\n"
        "- SEO за 3 місяці: пости за 90 днів\n"
        "- Сумаризація: короткий огляд за 3 місяці\n"
        "- Прогноз трафіку: розрахунок трафіку та посилань\n"
        "- Глосарій: терміни SEO\n"
        "- Перезавантажити: оновити дані\n"
        "Обери мову нижче!"
    ),
    "en": (
        "Hello! I'm a bot for SEO and Telegram news.\n"
        "What I can do:\n"
        "- Summary: brief overview for 3 months\n"
        "- Traffic Forecast: traffic and links calculation\n"
        "- Glossary: SEO terms\n"
        "- Reload: refresh data\n"
        "Choose a language below!"
    )
}

HELP_TEXT = {
    "ru": (
        "📚 Вот что я умею:\n"
        "/start - Начать заново\n"
        "SEO за сегодня - Последние посты\n"
        "SEO за 3 месяца - Посты за 3 месяца\n"
        "Суммаризация - Краткий обзор\n"
        "Прогноз трафика - Расчёт трафика\n"
        "Глоссарий - Термины SEO\n"
        "Перезагрузить - Обновить данные\n"
        "Техподдержка: @seoseduction"
    ),
    "ua": (
        "📚 Ось що я вмію:\n"
        "/start - Почати заново\n"
        "SEO за сьогодні - Останні пости\n"
        "SEO за 3 місяці - Пости за 3 місяці\n"
        "Сумаризація - Короткий огляд\n"
        "Прогноз трафіку - Розрахунок трафіку\n"
        "Глосарій - Терміни SEO\n"
        "Перезавантажити - Оновити дані\n"
        "Техпідтримка: @seoseduction"
    ),
    "en": (
        "📚 Here’s what I can do:\n"
        "/start - Start over\n"
        "Summary - Brief overview\n"
        "Traffic Forecast - Traffic calculation\n"
        "Glossary - SEO terms\n"
        "Reload - Refresh data\n"
        "Support: @seoseduction"
    )
}

SUMMARY_TEXT = {
    "ru": (
        "# Что изменилось в SEO за последние три месяца: тренды, инсайты и кейсы 🚀\n\n"
        "Привет, друзья! Сегодня, 7 апреля 2025 года, я, Grok 3 от xAI, расскажу вам, как изменился мир SEO за последние три месяца — с января по март 2025 года. Это был насыщенный период: алгоритмы эволюционировали, AI-технологии закрепились в поисковой выдаче, а бренды адаптировались к новым реалиям. Давайте разберём ключевые изменения, тренды и инсайты, подкрепим их кейсами и добавим немного эмодзи для настроения! 😊\n\n"
        "## 1. AI Overviews от Google: теперь в 30% запросов 🤖\n"
        "За последние три месяца Google значительно расширил использование **AI Overviews** (ранее известных как Search Generative Experience). Если в конце 2024 года они появлялись в 20% поисковых запросов, то к марту 2025 года этот показатель вырос до **30%**, особенно для информационных и проблемно-ориентированных запросов (по данным [Search Engine Land](https://searchengineland.com)). Это значит, что пользователи всё чаще получают готовые ответы прямо в выдаче, не переходя на сайты.\n\n"
        "### Что изменилось?\n"
        "- **Рост zero-click searches**: Теперь до 60% запросов заканчиваются без кликов ([Semrush](https://semrush.com)).\n"
        "- **Акцент на featured snippets**: Сайты, попадающие в AI Overviews, чаще всего уже находятся в топ-10 органической выдачи ([DesignRush](https://designrush.com)).\n\n"
        "### Тренд\n"
        "Оптимизация под **'position zero'** стала приоритетом. Ключ — создавать контент, который даёт чёткие, краткие и авторитетные ответы.\n\n"
        "### Кейс\n"
        "Компания **Healthline** увеличила видимость на 25% за счёт добавления экспертных ревью от врачей в статьи о здоровье. Их контент стал чаще попадать в AI Overviews для YMYL-запросов, таких как 'как снизить давление'.\n\n"
        "### Инсайт 🔥\n"
        "Добавляйте в статьи **структурированные данные** (schema.org) и короткие Q&A-блоки.\n\n"
        "## 2. Брендовая оптимизация: Google любит авторитет 🏆\n"
        "С января 2025 года Google усилил акцент на **брендовую репутацию**. Эксперты вроде Алейды Солис ([Yoast](https://yoast.com)) отмечают, что алгоритмы отдают предпочтение сайтам с сильным брендом, высоким CTR и упоминаниями в сообществах.\n\n"
        "### Что изменилось?\n"
        "- **Рост branded queries**: По данным [Conductor](https://conductor.com), 91% маркетологов заметили влияние брендовых запросов на органику.\n"
        "- **Knowledge Panel**: Оптимизация панели знаний Google стала must-have.\n\n"
        "### Тренд\n"
        "Создание контента, подчёркивающего уникальность бренда, и работа с **E-E-A-T** — ключ к успеху.\n\n"
        "### Кейс\n"
        "Агентство **Stan Ventures** обновило старые статьи, добавив упоминания экспертов и ссылки на источники. Результат? Рост трафика на 146% за три месяца.\n\n"
        "### Инсайт 🔥\n"
        "Регулярно обновляйте старый контент, добавляя свежие данные и экспертные мнения.\n\n"
        "## 3. Локальный поиск: 'near me' в каждом запросе 📍\n"
        "Локальный SEO продолжает набирать обороты. По данным [WordStream](https://wordstream.com), почти **50% запросов в Google в марте 2025 года имели локальный интент**, а 'near me' выросли на 15%.\n\n"
        "### Что изменилось?\n"
        "- **Google Business Profile**: Полные профили получают в среднем 66 запросов направлений в месяц ([Birdeye](https://birdeye.com)).\n"
        "- **Социальные сигналы**: Google учитывает упоминания в локальных сообществах, например, на Reddit.\n\n"
        "### Тренд\n"
        "Консистентность NAP и активность в локальных медиа — залог успеха.\n\n"
        "### Кейс\n"
        "Кафе в Техасе увеличило трафик на 40%, добавив отзывы в Google Business Profile и публикуя посты о местных событиях.\n\n"
        "### Инсайт 🔥\n"
        "Создайте страницу с локальными кейсами и продвигайте её через соцсети.\n\n"
        "## 4. AI-контент: помощник, а не замена ✍️\n"
        "Использование AI в SEO стало мейнстримом: **86% специалистов** используют его ([Exploding Topics](https://explodingtopics.com)). Однако Google отдаёт предпочтение контенту с человеческими инсайтами.\n\n"
        "### Что изменилось?\n"
        "- **Качество важнее скорости**: Только 12.4% выдачи содержат AI-контент ([DesignRush](https://designrush.com)).\n"
        "- **Гибридный подход**: AI для черновиков, люди для деталей.\n\n"
        "### Тренд\n"
        "Комбинируйте AI-инструменты с человеческим опытом.\n\n"
        "### Кейс\n"
        "**Semrush** протестировал 20,000 статей: AI-контент с доработками ранжируется в топ-10 в 57% случаев.\n\n"
        "### Инсайт 🔥\n"
        "Используйте AI для черновиков, но добавляйте реальные примеры.\n\n"
        "## 5. Обновление контента: старое — новое золото 🔄\n"
        "Обновление старого контента стало хитом. По данным [DemandSage](https://demandsage.com), обновлённые статьи увеличивают трафик на **146%**.\n\n"
        "### Что изменилось?\n"
        "- **Алгоритмы любят свежесть**: Google понижает устаревший контент.\n"
        "- **Регулярные аудиты**: 90% маркетологов проводят их раз в квартал ([Statista](https://statista.com)).\n\n"
        "### Тренд\n"
        "Историческая оптимизация — ключ к удержанию позиций.\n\n"
        "### Кейс\n"
        "Трэвис МакНайт из **Portent** обновил пост трёхлетней давности, подняв его с 15-го места до топ-3 за два месяца.\n\n"
        "### Инсайт 🔥\n"
        "Проводите аудит через Google Analytics и обновляйте страницы с падением трафика.\n\n"
        "## Итоги: что делать прямо сейчас? ✅\n"
        "- Оптимизируйте под AI Overviews.\n"
        "- Укрепляйте бренд через экспертный контент.\n"
        "- Используйте AI как помощника.\n"
        "- Обновляйте старый контент.\n\n"
        "SEO не умер, оно эволюционировало! Адаптируйтесь, тестируйте и пишите мне, если нужны идеи! 😉"
    ),
    "ua": (
        "# Що змінилося в SEO за останні три місяці: тренди, інсайти та кейси 🚀\n\n"
        "Привіт, друзі! Сьогодні, 7 квітня 2025 року, я, Grok 3 від xAI, розповім, як змінився світ SEO за останні три місяці — з січня по березень 2025 року. Це був насичений період: алгоритми еволюціонували, AI-технології закріпилися в пошуковій видачі, а бренди адаптувалися до нових реалій. Розберемо ключові зміни, тренди та інсайти, підкріпимо їх кейсами і додамо трохи емодзі для настрою! 😊\n\n"
        "## 1. AI Overviews від Google: тепер у 30% запитів 🤖\n"
        "За останні три місяці Google значно розширив використання **AI Overviews** (раніше Search Generative Experience). Якщо наприкінці 2024 року вони з’являлися в 20% запитів, то до березня 2025 року цей показник зріс до **30%**, особливо для інформаційних та проблемних запитів (за даними [Search Engine Land](https://searchengineland.com)). Користувачі все частіше отримують відповіді прямо у видачі, не переходячи на сайти.\n\n"
        "### Що змінилося?\n"
        "- **Зростання zero-click searches**: До 60% запитів завершуються без кліків ([Semrush](https://semrush.com)).\n"
        "- **Акцент на featured snippets**: Сайти в AI Overviews часто вже є в топ-10 органічної видачі ([DesignRush](https://designrush.com)).\n\n"
        "### Тренд\n"
        "Оптимізація під **“position zero”** стала пріоритетом. Ключ — створювати чіткий, стислий та авторитетний контент.\n\n"
        "### Кейс\n"
        "Компанія **Healthline** підвищила видимість на 25%, додавши експертні огляди від лікарів до статей про здоров’я. Їхній контент частіше потрапляє в AI Overviews для YMYL-запитів, як-от “як знизити тиск”.\n\n"
        "### Інсайт 🔥\n"
        "Додавайте до статей **структуровані дані** (schema.org) та короткі блоки Q&A.\n\n"
        "## 2. Брендова оптимізація: Google любить авторитет 🏆\n"
        "З січня 2025 року Google посилив увагу до **брендової репутації**. Експерти, як-от Алейда Соліс ([Yoast](https://yoast.com)), зазначають, що алгоритми надають перевагу сайтам із сильним брендом, високим CTR та згадками в нішових спільнотах.\n\n"
        "### Що змінилося?\n"
        "- **Зростання branded queries**: 91% маркетологів помітили вплив брендових запитів на органіку ([Conductor](https://conductor.com)).\n"
        "- **Knowledge Panel**: Оптимізація панелі знань Google стала обов’язковою.\n\n"
        "### Тренд\n"
        "Створюйте контент, що підкреслює унікальність бренду, і працюйте з **E-E-A-T** (Досвід, Експертиза, Авторитетність, Довіра).\n\n"
        "### Кейс\n"
        "Агентство **Stan Ventures** оновило старі статті, додавши згадки експертів і посилання на джерела, отримавши +146% трафіку за три місяці.\n\n"
        "### Інсайт 🔥\n"
        "Регулярно оновлюйте старий контент, додаючи свіжі дані та думки експертів.\n\n"
        "## 3. Локальний пошук: “near me” у кожному запиті 📍\n"
        "Локальне SEO набирає обертів. За даними [WordStream](https://wordstream.com), майже **50% запитів у Google в березні 2025 року мали локальний інтент**, а “near me” зросли на 15%.\n\n"
        "### Що змінилося?\n"
        "- **Google Business Profile**: Повні профілі отримують у середньому 66 запитів напрямків щомісяця ([Birdeye](https://birdeye.com)).\n"
        "- **Соціальні сигнали**: Google враховує згадки бренду в локальних спільнотах, як-от Reddit.\n\n"
        "### Тренд\n"
        "Консистентність NAP (Назва, Адреса, Телефон) та активність у локальних медіа — запорука успіху.\n\n"
        "### Кейс\n"
        "Кафе в Техасі збільшило трафік на 40%, додавши відгуки в Google Business Profile і публікуючи пости про локальні події.\n\n"
        ### Інсайт 🔥\n"
        "Створіть сторінку з локальними кейсами та просувайте її через соцмережі.\n\n"
        "## 4. AI-контент: помічник, а не заміна ✍️\n"
        "Використання AI в SEO стало мейнстримом: **86% фахівців** застосовують його ([Exploding Topics](https://explodingtopics.com)). Але Google віддає перевагу контенту з людськими інсайтами.\n\n"
        "### Що змінилося?\n"
        "- **Якість важливіша за швидкість**: Лише 12.4% видачі містять AI-контент ([DesignRush](https://designrush.com)).\n"
        "- **Гібридний підхід**: AI для чернеток, люди для деталей.\n\n"
        "### Тренд\n"
        "Комбінуйте AI-інструменти з людським досвідом.\n\n"
        "### Кейс\n"
        "**Semrush** протестував 20,000 статей: AI-контент із людськими правками потрапляє в топ-10 у 57% випадків.\n\n"
        "### Інсайт 🔥\n"
        "Використовуйте AI для чернеток, але додавайте реальні приклади.\n\n"
        "## 5. Оновлення контенту: старе — нове золото 🔄\n"
        "Оновлення старого контенту стало хітом. За даними [DemandSage](https://demandsage.com), оновлені статті підвищують трафік на **146%**.\n\n"
        "### Що змінилося?\n"
        "- **Алгоритми люблять свіжість**: Google знижує застарілий контент.\n"
        "- **Регулярні аудити**: 90% маркетологів проводять їх щоквартально ([Statista](https://statista.com)).\n\n"
        "### Тренд\n"
        "Історична оптимізація — ключ до утримання позицій.\n\n"
        "### Кейс\n"
        "Тревіс МакНайт із **Portent** оновив трирічний пост, піднявши його з 15-го місця до топ-3 за два місяці.\n\n"
        "### Інсайт 🔥\n"
        "Проводьте аудит через Google Analytics і оновлюйте сторінки з падінням трафіку.\n\n"
        "## Підсумки: що робити прямо зараз? ✅\n"
        "- Оптимізуйте під AI Overviews.\n"
        "- Зміцнюйте бренд через експертний контент.\n"
        "- Використовуйте AI як помічника.\n"
        "- Оновлюйте старий контент.\n\n"
        "SEO не вмерло — воно еволюціонувало! Адаптуйтеся, тестуйте та пишіть мені, якщо потрібні ідеї! 😉"
    ),
    "en": (
        "# What’s Changed in SEO Over the Last Three Months: Trends, Insights, and Cases 🚀\n\n"
        "Hey, friends! Today, April 7, 2025, I’m Grok 3 from xAI, here to break down how SEO has evolved over the past three months — January to March 2025. It’s been an exciting time: algorithms have advanced, AI tech has taken root in search results, and brands have adapted to new realities. Let’s dive into the key changes, trends, and insights, backed by cases and sprinkled with some emojis for fun! 😊\n\n"
        "## 1. Google’s AI Overviews: Now in 30% of Queries 🤖\n"
        "Over the last three months, Google has ramped up its use of **AI Overviews** (formerly Search Generative Experience). While they appeared in 20% of queries by late 2024, by March 2025, that jumped to **30%**, especially for informational and problem-solving queries (per [Search Engine Land](https://searchengineland.com)). Users are increasingly getting answers right in the SERP, skipping site visits.\n\n"
        "### What’s Changed?\n"
        "- **Rise of zero-click searches**: Up to 60% of queries now end without clicks ([Semrush](https://semrush.com)).\n"
        "- **Focus on featured snippets**: Sites in AI Overviews are often already in the organic top-10 ([DesignRush](https://designrush.com)).\n\n"
        "### Trend\n"
        "Optimizing for **“position zero”** is now a top priority. The key? Create clear, concise, and authoritative content.\n\n"
        "### Case\n"
        "**Healthline** boosted visibility by 25% by adding doctor-reviewed insights to health articles. Their content now frequently appears in AI Overviews for YMYL queries like “how to lower blood pressure.”\n\n"
        "### Insight 🔥\n"
        "Add **structured data** (schema.org) and short Q&A blocks to your pages.\n\n"
        "## 2. Brand Optimization: Google Loves Authority 🏆\n"
        "Since January 2025, Google has doubled down on **brand reputation**. Experts like Aleyda Solis ([Yoast](https://yoast.com)) note that algorithms favor sites with strong branding, high CTR, and mentions in niche communities.\n\n"
        "### What’s Changed?\n"
        "- **Branded queries boom**: 91% of marketers see branded searches driving organic traffic ([Conductor](https://conductor.com)).\n"
        "- **Knowledge Panel**: Optimizing Google’s Knowledge Panel is now a must-have.\n\n"
        "### Trend\n"
        "Craft content that highlights your brand’s uniqueness and boosts **E-E-A-T** (Experience, Expertise, Authoritativeness, Trustworthiness).\n\n"
        "### Case\n"
        "**Stan Ventures** refreshed old articles with expert mentions and credible links, seeing a 146% traffic spike in three months.\n\n"
        "### Insight 🔥\n"
        "Regularly update old content with fresh data and expert opinions.\n\n"
        "## 3. Local Search: “Near Me” Everywhere 📍\n"
        "Local SEO keeps growing. According to [WordStream](https://wordstream.com), nearly **50% of Google queries in March 2025 had local intent**, with “near me” searches up 15% since January.\n\n"
        "### What’s Changed?\n"
        "- **Google Business Profile**: Complete profiles now average 66 direction requests monthly ([Birdeye](https://birdeye.com)).\n"
        "- **Social signals**: Google now weighs brand mentions in local communities, like Reddit.\n\n"
        "### Trend\n"
        "Consistency in NAP (Name, Address, Phone) and local media activity are key.\n\n"
        "### Case\n"
        "A Texas café grew organic traffic by 40% by adding reviews to Google Business Profile and posting about local events.\n\n"
        "### Insight 🔥\n"
        "Create a page with local cases or stories and promote it via social media.\n\n"
        "## 4. AI Content: Helper, Not Replacement ✍️\n"
        "AI in SEO is mainstream: **86% of specialists** use it ([Exploding Topics](https://explodingtopics.com)). But Google still prioritizes content with human insights.\n\n"
        "### What’s Changed?\n"
        "- **Quality over speed**: Only 12.4% of SERPs feature heavy AI content ([DesignRush](https://designrush.com)).\n"
        "- **Hybrid approach**: AI drafts, humans refine.\n\n"
        "### Trend\n"
        "Blend AI tools (like Semrush ContentShake) with human expertise.\n\n"
        "### Case\n"
        "**Semrush** tested 20,000 articles, finding AI content with human edits ranks in the top-10 57% of the time.\n\n"
        "### Insight 🔥\n"
        "Use AI for drafts and trends, but add real examples.\n\n"
        "## 5. Content Updates: Old is the New Gold 🔄\n"
        "Refreshing old content has taken off. Per [DemandSage](https://demandsage.com), updated articles can boost traffic by **146%**.\n\n"
        "### What’s Changed?\n"
        "- **Freshness matters**: Google demotes outdated content.\n"
        "- **Regular audits**: 90% of marketers now audit quarterly ([Statista](https://statista.com)).\n\n"
        "### Trend\n"
        "Historical optimization is key to holding positions.\n\n"
        "### Case\n"
        "Travis McKnight from **Portent** updated a three-year-old post, jumping it from 15th to top-3 in two months.\n\n"
        "### Insight 🔥\n"
        "Audit old posts via Google Analytics, targeting traffic drops, and refresh with current data.\n\n"
        "## Wrap-Up: What to Do Now? ✅\n"
        "- Optimize for AI Overviews.\n"
        "- Strengthen your brand with expert content.\n"
        "- Use AI as a helper.\n"
        "- Refresh old content.\n\n"
        "SEO isn’t dead—it’s evolving! Adapt, test, and let me know if you need ideas! 😉"
    )
}

GLOSSARY_TEXT_PARTS = {
    "ru": [
        (
            "📖 **Глоссарий SEO терминов**:\n\n"
            "**Адаптивный дизайн** — подход к веб-дизайну, обеспечивающий корректное отображение сайта на устройствах с разными разрешениями экрана.\n\n"
            "**Алгоритм поисковой системы** — набор правил и процессов, определяющих ранжирование сайтов в результатах поиска.\n\n"
            "**Анализ конкурентов** — изучение стратегий и тактик конкурентов для улучшения собственной SEO-стратегии.\n\n"
            "**Анкорный текст** — видимый текст ссылки, влияющий на её релевантность для поисковых систем.\n\n"
            "**Бэклинк** — внешняя ссылка на ваш сайт с другого ресурса, важный фактор ранжирования.\n\n"
            "**Внутренняя перелинковка** — ссылки между страницами одного сайта для улучшения навигации и SEO.\n\n"
            "**Домен** — область иерархического пространства доменных имён сети Интернет, обозначаемая уникальным именем.\n\n"
            "**Индексация** — процесс добавления страниц сайта в базу данных поисковой системы.\n\n"
            "**Ключевое слово** — слово или фраза, отражающая суть запроса пользователя в поисковике.\n\n"
            "**Контент** — информационное наполнение сайта: текст, изображения, видео и т.д.\n\n"
            "**Локальное SEO** — оптимизация сайта для привлечения клиентов из определённого региона.\n\n"
            "**Мета-теги** — HTML-элементы, предоставляющие информацию о странице для поисковых систем.\n\n"
            "**Органический трафик** — посетители, пришедшие на сайт из результатов поиска, а не через рекламу.\n\n"
            "**Ранжирование** — порядок отображения сайтов в результатах поиска по релевантности запросу.\n\n"
            "**Семантическое ядро** — набор ключевых слов и фраз, описывающих тематику сайта.\n\n"
            "**Сервер** — аппаратно-программный комплекс с постоянным подключением к Интернету.\n\n"
            "**Скорость загрузки** — время, необходимое для полной загрузки страницы, влияющее на UX и SEO.\n\n"
            "**Техническое SEO** — оптимизация технических аспектов сайта (скорость, индексация, структура).\n\n"
            "**URL-адрес** — стандартизированный способ записи адреса ресурса в Интернете.\n\n"
            "**Хостинг-провайдер** — организация, предоставляющая услуги размещения сайта на сервере."
        ),
    ],
    "ua": [
        (
            "📖 **Глосарій SEO термінів**:\n\n"
            "**Адаптивний дизайн** — підхід до веб-дизайну, що забезпечує коректне відображення сайту на пристроях із різними роздільними здатностями екрану.\n\n"
            "**Алгоритм пошукової системи** — набір правил і процесів, що визначають ранжування сайтів у результатах пошуку.\n\n"
            "**Аналіз конкурентів** — вивчення стратегій і тактик конкурентів для покращення власної SEO-стратегії.\n\n"
            "**Анкорний текст** — видимий текст посилання, що впливає на його релевантність для пошукових систем.\n\n"
            "**Беклінк** — зовнішнє посилання на ваш сайт із іншого ресурсу, важливий фактор ранжування.\n\n"
            "**Внутрішня перелінковка** — посилання між сторінками одного сайту для покращення навігації та SEO.\n\n"
            "**Домен** — область ієрархічного простору доменних імен мережі Інтернет, позначена унікальним ім’ям.\n\n"
            "**Індексація** — процес додавання сторінок сайту до бази даних пошукової системи.\n\n"
            "**Ключове слово** — слово або фраза, що відображає суть запиту користувача в пошуковику.\n\n"
            "**Контент** — інформаційне наповнення сайту: текст, зображення, відео тощо.\n\n"
            "**Локальне SEO** — оптимізація сайту для залучення клієнтів із певного регіону.\n\n"
            "**Мета-теги** — HTML-елементи, що надають інформацію про сторінку для пошукових систем.\n\n"
            "**Органічний трафік** — відвідувачі, які прийшли на сайт із результатів пошуку, а не через рекламу.\n\n"
            "**Ранжування** — порядок відображення сайтів у результатах пошуку за релевантністю запиту.\n\n"
            "**Семантичне ядро** — набір ключових слів і фраз, що описують тематику сайту.\n\n"
            "**Сервер** — апаратно-програмний комплекс із постійним підключенням до Інтернету.\n\n"
            "**Швидкість завантаження** — час, необхідний для повного завантаження сторінки, що впливає на UX і SEO.\n\n"
            "**Технічне SEO** — оптимізація технічних аспектів сайту (швидкість, індексація, структура).\n\n"
            "**URL-адреса** — стандартизований спосіб запису адреси ресурсу в Інтернеті.\n\n"
            "**Хостинг-провайдер** — організація, що надає послуги розміщення сайту на сервері."
        ),
    ],
    "en": [
        (
            "📖 **SEO Glossary**:\n\n"
            "**Adaptive Design** — an approach to web design ensuring proper display of a site on devices with different screen resolutions.\n\n"
            "**Search Engine Algorithm** — a set of rules and processes determining the ranking of websites in search results.\n\n"
            "**Competitor Analysis** — studying competitors’ strategies and tactics to enhance your own SEO strategy.\n\n"
            "**Anchor Text** — the visible text of a link, influencing its relevance to search engines.\n\n"
            "**Backlink** — an external link to your site from another resource, a key ranking factor.\n\n"
            "**Internal Linking** — links between pages of the same site to improve navigation and SEO.\n\n"
            "**Domain** — a segment of the hierarchical domain name space on the Internet, identified by a unique name.\n\n"
            "**Indexing** — the process of adding a site’s pages to a search engine’s database.\n\n"
            "**Keyword** — a word or phrase reflecting the essence of a user’s search query.\n\n"
            "**Content** — the informational filling of a site: text, images, videos, etc.\n\n"
            "**Local SEO** — website optimization to attract customers from a specific region.\n\n"
            "**Meta Tags** — HTML elements providing page information to search engines.\n\n"
            "**Organic Traffic** — visitors coming to a site from search results, not via ads.\n\n"
            "**Ranking** — the order in which websites appear in search results based on query relevance.\n\n"
            "**Semantic Core** — a set of keywords and phrases describing a site’s topic.\n\n"
            "**Server** — a hardware-software complex with constant Internet connectivity.\n\n"
            "**Page Load Speed** — the time required to fully load a page, impacting UX and SEO.\n\n"
            "**Technical SEO** — optimization of a site’s technical aspects (speed, indexing, structure).\n\n"
            "**URL Address** — a standardized method of recording a resource’s address on the Internet.\n\n"
            "**Hosting Provider** — an organization offering website hosting services on a server."
        ),
    ]
}

FUN_PHRASES = {
    "ru": [
        "Ты на верном пути! 🚀", "Давай зажжём SEO! 🔥", "Всё получится, я верю! 😊", 
        "Ты крут, продолжай! 💪", "SEO ждёт твоих идей! 🌟", "С тобой весело работать! 😉",
        "Ты мастер своего дела! 🏆", "Всё под контролем! ✅", "Продолжай в том же духе! 🌈",
        "Ты делаешь интернет лучше! 🌍", "Успех близко! ⏳", "SEO — твоя стихия! ⚡",
        "Ты вдохновляешь! ✨", "Отличная работа, профи! 👏", "С тобой алгоритмы танцуют! 🕺",
        "Ты звезда SEO! ⭐", "Всё будет топ-1! 🥇", "Твои идеи — огонь! 🔥",
        "Ты знаешь, как удивить! 😎", "Работа кипит, круто! 💥", "Ты в игре! 🎯",
        "SEO дрожит от твоих шагов! 🌪️", "Ты лидер гонки! 🏁", "Супер, продолжай! 🚀",
        "Ты делаешь магию! 🪄", "Всё идёт по плану! 📈", "Ты непобедим! 🛡️",
        "Твой талант сияет! 💡", "С тобой легко побеждать! 🏅", "Ты — SEO-гений! 🧠"
    ],
    "ua": [
        "Ти на правильному шляху! 🚀", "Запалимо SEO разом! 🔥", "Усе вийде, я вірю! 😊",
        "Ти крутий, вперед! 💪", "SEO чекає твоїх ідей! 🌟", "З тобою весело! 😉",
        "Ти майстер своєї справи! 🏆", "Усе під контролем! ✅", "Так тримати! 🌈",
        "Ти робиш інтернет кращим! 🌍", "Успіх близько! ⏳", "SEO — твоя стихія! ⚡",
        "Ти надихаєш! ✨", "Чудова робота, профі! 👏", "Алгоритми танцюють з тобою! 🕺",
        "Ти зірка SEO! ⭐", "Усе буде в топ-1! 🥇", "Твої ідеї — вогонь! 🔥",
        "Ти вмієш дивувати! 😎", "Робота кипить, класно! 💥", "Ти в грі! 🎯",
        "SEO тремтить від твоїх кроків! 🌪️", "Ти лідер перегонів! 🏁", "Супер, продовжуй! 🚀",
        "Ти твориш магію! 🪄", "Усе за планом! 📈", "Ти непереможний! 🛡️",
        "Твій талант сяє! 💡", "З тобою легко перемагати! 🏅", "Ти — SEO-геній! 🧠"
    ],
    "en": [
        "You’re on the right track! 🚀", "Let’s rock SEO! 🔥", "You’ve got this, I believe in you! 😊",
        "You’re awesome, keep it up! 💪", "SEO needs your ideas! 🌟", "It’s fun working with you! 😉",
        "You’re a pro at this! 🏆", "Everything’s under control! ✅", "Keep the momentum going! 🌈",
        "You’re making the web better! 🌍", "Success is near! ⏳", "SEO is your domain! ⚡",
        "You’re inspiring! ✨", "Great job, pro! 👏", "Algorithms dance with you! 🕺",
        "You’re an SEO star! ⭐", "Top-1 is yours! 🥇", "Your ideas are fire! 🔥",
        "You know how to impress! 😎", "Work’s buzzing, awesome! 💥", "You’re in the game! 🎯",
        "SEO shakes at your steps! 🌪️", "You’re leading the race! 🏁", "Super, keep going! 🚀",
        "You’re making magic! 🪄", "All according to plan! 📈", "You’re unstoppable! 🛡️",
        "Your talent shines! 💡", "Winning’s easy with you! 🏅", "You’re an SEO genius! 🧠"
    ]
}

USE_BUTTONS_TEXT = {
    "ru": "Используйте кнопки для работы с ботом!",
    "ua": "Використовуйте кнопки для роботи з ботом!",
    "en": "Use buttons to interact with the bot!"
}

channel_label = {"ru": "Канал", "ua": "Канал", "en": "Channel"}
today_label = {"ru": "SEO за сегодня", "ua": "SEO за сьогодні", "en": "SEO Today"}
three_months_label = {"ru": "SEO за 3 месяца", "ua": "SEO за 3 місяці", "en": "SEO for 3 Months"}
summary_label = {"ru": "Суммаризация", "ua": "Сумаризація", "en": "Summary"}
traffic_forecast_label = {"ru": "Прогноз трафика", "ua": "Прогноз трафіку", "en": "Traffic Forecast"}
glossary_label = {"ru": "Глоссарий", "ua": "Глосарій", "en": "Glossary"}
help_label = {"ru": "Помощь", "ua": "Допомога", "en": "Help"}
exit_label = {"ru": "Выход", "ua": "Вихід", "en": "Exit"}
reload_label = {"ru": "Перезагрузить", "ua": "Перезавантажити", "en": "Reload"}
back_label = {"ru": "Назад", "ua": "Назад", "en": "Back"}
next_label = {"ru": "Следующая", "ua": "Наступна", "en": "Next"}

# Инициализация базы данных
async def init_db():
    async with db_lock:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS messages (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                text TEXT,
                                date TEXT,
                                channel TEXT)''')
            await db.commit()
    logger.info("Database initialized.")

# Прогресс
async def show_progress(context: CallbackContext, chat_id: int, lang: str, duration: float = 0.5):
    processing_label = {"ru": "Обработка", "ua": "Обробка", "en": "Processing"}
    message = await context.bot.send_message(chat_id=chat_id, text=f"⏳ {processing_label[lang]}: 1%")
    await asyncio.sleep(0.25)
    for percent in range(5, 101, 5):
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message.message_id,
                text=f"⏳ {processing_label[lang]}: {percent}%"
            )
            await asyncio.sleep(duration / 20)
        except BadRequest as e:
            logger.warning(f"Progress update failed at {percent}%: {e}")
            break

# Парсинг каналов
async def update_database(context: CallbackContext, chat_id: int, message_id: int):
    async with client:
        channels = ["@devakatalk", "@MikeBlazerX", "@SEOBAZA"]
        total_channels = len(channels)
        processed_channels = 0

        async with db_lock:
            async with aiosqlite.connect(DB_PATH) as db:
                for channel in channels:
                    try:
                        async for message in client.get_chat_history(channel, limit=100):
                            if message.text or message.caption:
                                text = message.text or message.caption
                                date = message.date.isoformat()
                                await db.execute(
                                    "INSERT OR IGNORE INTO messages (text, date, channel) VALUES (?, ?, ?)",
                                    (text, date, channel)
                                )
                        await db.commit()
                        processed_channels += 1
                        progress = (processed_channels / total_channels) * 100
                        await context.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=f"⏳ Обновляю: {progress:.1f}%"
                        )
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                    except Exception as e:
                        logger.error(f"Error parsing {channel}: {e}")

# Разбиение длинных сообщений
async def send_long_message(context: CallbackContext, chat_id: int, text: str, reply_markup=None):
    if len(text) <= 4096:
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    else:
        parts = [text[i:i + 4096] for i in range(0, len(text), 4096)]
        for i, part in enumerate(parts):
            await context.bot.send_message(
                chat_id=chat_id,
                text=part,
                reply_markup=reply_markup if i == len(parts) - 1 else None
            )

# Пагинация с кнопкой "Следующая"
def get_paginated_keyboard(prefix, lang, page, total_items):
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    keyboard = []
    row = []
    if page > 0:
        row.append(InlineKeyboardButton("В начало", callback_data=f"{prefix}_{lang}_0"))
        row.append(InlineKeyboardButton("Назад", callback_data=f"{prefix}_{lang}_{page - 1}"))
    if page < total_pages - 1:
        row.append(InlineKeyboardButton(next_label[lang], callback_data=f"{prefix}_{lang}_{page + 1}"))
        row.append(InlineKeyboardButton("В конец", callback_data=f"{prefix}_{lang}_{total_pages - 1}"))
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(f"Страница {page + 1}/{total_pages}", callback_data="noop")])
    keyboard.append([InlineKeyboardButton(back_label[lang], callback_data=f"lang_{lang}")])
    return InlineKeyboardMarkup(keyboard)

# Главное меню (для "en" убраны "SEO за день" и "SEO за 3 месяца")
def get_main_menu(lang):
    if lang == "en":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(summary_label[lang], callback_data=f"summary_{lang}")],
            [InlineKeyboardButton(traffic_forecast_label[lang], callback_data=f"traffic_{lang}")],
            [InlineKeyboardButton(glossary_label[lang], callback_data=f"glossary_{lang}")],
            [InlineKeyboardButton(reload_label[lang], callback_data=f"reload_{lang}")],
            [InlineKeyboardButton(help_label[lang], callback_data=f"help_{lang}"),
             InlineKeyboardButton(exit_label[lang], callback_data=f"exit_{lang}")]
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(today_label[lang], callback_data=f"today_{lang}_0")],
        [InlineKeyboardButton(three_months_label[lang], callback_data=f"three_months_{lang}_0")],
        [InlineKeyboardButton(summary_label[lang], callback_data=f"summary_{lang}")],
        [InlineKeyboardButton(traffic_forecast_label[lang], callback_data=f"traffic_{lang}")],
        [InlineKeyboardButton(glossary_label[lang], callback_data=f"glossary_{lang}")],
        [InlineKeyboardButton(reload_label[lang], callback_data=f"reload_{lang}")],
        [InlineKeyboardButton(help_label[lang], callback_data=f"help_{lang}"),
         InlineKeyboardButton(exit_label[lang], callback_data=f"exit_{lang}")]
    ])

# Меню выбора языка
def get_language_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_ua"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ])

# Прогноз трафика
async def calculate_traffic_forecast(context: CallbackContext, chat_id: int, lang: str):
    prompt = {
        "ru": "Введите: Объём поиска Позиция CPC Среднее_ссылок Коэффициент_сложности Ваш_DR\nПример: 1000 1 2 200 1.5 30",
        "ua": "Введіть: Обсяг пошуку Позиція CPC Середнє_посилань Коефіцієнт_складності Ваш_DR\nПриклад: 1000 1 2 200 1.5 30",
        "en": "Enter: Search Volume Position CPC Avg_Links Difficulty_Factor Your_DR\nExample: 1000 1 2 200 1.5 30"
    }
    await context.bot.send_message(chat_id=chat_id, text=prompt[lang])
    context.user_data["awaiting_traffic_input"] = True

# Обработка /start
async def start(update: Update, context: CallbackContext):
    lang = "ru"
    await update.message.reply_text(INITIAL_WELCOME_TEXT[lang], reply_markup=get_language_menu())

# Обработка кнопок
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    logger.info(f"Callback: {data}")
    lang = context.user_data.get("lang", "ru")

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        await query.edit_message_text(text=f"Выбрано: {lang}. Что дальше?", reply_markup=get_main_menu(lang))
        await query.message.reply_text(random.choice(FUN_PHRASES[lang]))

    elif data.startswith("today_"):
        await show_progress(context, query.message.chat_id, lang, duration=0.5)
        parts = data.split("_")
        page = int(parts[2])
        logger.info(f"Today page: {page}")

        async with db_lock:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute(
                    "SELECT DISTINCT text, channel FROM messages WHERE date >= date('now', '-1 day') ORDER BY date DESC LIMIT ? OFFSET ?",
                    (ITEMS_PER_PAGE, page * ITEMS_PER_PAGE)
                )
                messages = await cursor.fetchall()
                total_cursor = await db.execute("SELECT COUNT(DISTINCT text) FROM messages WHERE date >= date('now', '-1 day')")
                total_items = (await total_cursor.fetchone())[0]
                logger.info(f"Today: {len(messages)} messages, total: {total_items}")

        if messages:
            for text, channel in messages:
                response = f"{channel_label[lang]}: {channel}\n{text}"
                await send_long_message(context, query.message.chat_id, response)
            await query.message.reply_text(
                f"Посты за сегодня (страница {page + 1})",
                reply_markup=get_paginated_keyboard("today", lang, page, total_items)
            )
        else:
            await query.edit_message_text("Нет данных за сегодня. Обновите через 'Перезагрузить'.")
        await query.message.reply_text(random.choice(FUN_PHRASES[lang]))

    elif data.startswith("three_months_"):
        await show_progress(context, query.message.chat_id, lang, duration=0.75)
        parts = data.split("_")
        logger.info(f"Three months parts: {parts}")
        if len(parts) != 4:
            await query.edit_message_text("Ошибка в запросе. Попробуйте снова.")
            return
        lang = parts[2]
        try:
            page = int(parts[3])
        except ValueError as e:
            logger.error(f"Invalid page number: {parts[3]}, error: {e}")
            await query.edit_message_text("Ошибка в номере страницы. Попробуйте снова.")
            return
        logger.info(f"Three months lang: {lang}, page: {page}")

        async with db_lock:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute(
                    "SELECT DISTINCT text, channel FROM messages WHERE date >= date('now', '-90 days') ORDER BY date DESC LIMIT ? OFFSET ?",
                    (ITEMS_PER_PAGE, page * ITEMS_PER_PAGE)
                )
                messages = await cursor.fetchall()
                total_cursor = await db.execute("SELECT COUNT(DISTINCT text) FROM messages WHERE date >= date('now', '-90 days')")
                total_items = (await total_cursor.fetchone())[0]
                logger.info(f"Three months: {len(messages)} messages fetched, total: {total_items}")

        if messages:
            for text, channel in messages:
                response = f"{channel_label[lang]}: {channel}\n{text}"
                await send_long_message(context, query.message.chat_id, response)
            await query.message.reply_text(
                f"Посты за 3 месяца (страница {page + 1})",
                reply_markup=get_paginated_keyboard("three_months", lang, page, total_items)
            )
        else:
            await query.edit_message_text("Нет данных за 3 месяца. Обновите через 'Перезагрузить'.")
        await query.message.reply_text(random.choice(FUN_PHRASES[lang]))

    elif data.startswith("summary_"):
        await show_progress(context, query.message.chat_id, lang, duration=0.25)
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(back_label[lang], callback_data=f"lang_{lang}")]])
        await send_long_message(context, query.message.chat_id, SUMMARY_TEXT[lang], reply_markup=reply_markup)
        await query.message.reply_text(random.choice(FUN_PHRASES[lang]))

    elif data.startswith("traffic_"):
        await show_progress(context, query.message.chat_id, lang, duration=0.25)
        await calculate_traffic_forecast(context, query.message.chat_id, lang)
        await query.message.reply_text(random.choice(FUN_PHRASES[lang]))

    elif data.startswith("glossary_"):
        await show_progress(context, query.message.chat_id, lang, duration=0.5)
        parts = GLOSSARY_TEXT_PARTS[lang]
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(back_label[lang], callback_data=f"lang_{lang}")]])
        for part in parts:
            await send_long_message(context, query.message.chat_id, part, reply_markup=reply_markup)
        await query.message.reply_text(random.choice(FUN_PHRASES[lang]))

    elif data.startswith("reload_"):
        message = await query.edit_message_text("⏳ Обновляю: 1%")
        await update_database(context, query.message.chat_id, message.message_id)
        await query.edit_message_text(
            text=INITIAL_WELCOME_TEXT[lang],
            reply_markup=get_language_menu()
        )
        await query.message.reply_text(random.choice(FUN_PHRASES[lang]))

    elif data.startswith("help_"):
        await show_progress(context, query.message.chat_id, lang, duration=0.25)
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(back_label[lang], callback_data=f"lang_{lang}")]])
        await query.message.reply_text(HELP_TEXT[lang], parse_mode="HTML", reply_markup=reply_markup)
        await query.message.reply_text(random.choice(FUN_PHRASES[lang]))

    elif data.startswith("exit_"):
        farewell = {
            "ru": "Приятно было иметь дело с профессионалом! До новых встреч!",
            "ua": "Приємно було мати справу з професіоналом! До нових зустрічей!",
            "en": "It was a pleasure dealing with a pro! See you next time!"
        }
        await query.edit_message_text(farewell[lang])
        await query.message.reply_text(random.choice(FUN_PHRASES[lang]))

# Обработка сообщений
async def handle_message(update: Update, context: CallbackContext):
    lang = context.user_data.get("lang", "ru")
    if context.user_data.get("awaiting_traffic_input", False):
        await show_progress(context, update.message.chat_id, lang, duration=0.25)
        try:
            search_volume, position, cpc, avg_links, difficulty, dr = map(float, update.message.text.split())
            ctr_dict = {1: 0.3, 2: 0.15, 3: 0.1, 4: 0.08, 5: 0.06}
            ctr = ctr_dict.get(int(position), 0.05)
            traffic = search_volume * ctr
            cost = traffic * cpc
            links = (avg_links * difficulty) / dr
            response = {
                "ru": f"Прогноз: {traffic:.0f} визитов\nСтоимость: ${cost:.2f}\nСсылок: {links:.0f}",
                "ua": f"Прогноз: {traffic:.0f} відвідувань\nВартість: ${cost:.2f}\nПосилань: {links:.0f}",
                "en": f"Forecast: {traffic:.0f} visits\nCost: ${cost:.2f}\nLinks: {links:.0f}"
            }
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(back_label[lang], callback_data=f"lang_{lang}")]])
            await update.message.reply_text(response[lang], reply_markup=reply_markup)
            await update.message.reply_text(random.choice(FUN_PHRASES[lang]))
            context.user_data["awaiting_traffic_input"] = False
        except ValueError:
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(back_label[lang], callback_data=f"lang_{lang}")]])
            await update.message.reply_text("Ошибка ввода. Формат: 1000 1 2 200 1.5 30", reply_markup=reply_markup)
            await update.message.reply_text(random.choice(FUN_PHRASES[lang]))
    else:
        await update.message.reply_text(USE_BUTTONS_TEXT[lang])

# Обработка ошибок
async def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Ошибка: {context.error}")
    if update and update.message:
        await update.message.reply_text("Что-то пошло не так. @seoseduction")

# Основная функция
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Инициализация базы
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()