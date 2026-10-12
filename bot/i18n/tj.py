TRANSLATIONS = {
    # General / Commands
    "start_welcome": (
        "👋 Ассалому алейкум, *{first_name}*!\n\n"
        "Ман боти ҳушманд барои баҳисобгирии даромад ва хароҷоти шахсӣ ҳастам 💰\n\n"
        "Шумо метавонед ба ман бо забони оддӣ паём фиристед, масалан:\n"
        "• _себ ба 10 сомонӣ харидам_\n"
        "• _такси 25 руб_\n"
        "• _хӯроки нисфирӯзӣ 15$_\n"
        "• _маош 500 доллар_\n\n"
        "Забони асосии асъори шумо: *{base_currency}*.\n"
        "Барои тағир додан асъорро интихоб кунед:"
    ),
    "menu_open": "Мурури асосӣ кушода шуд:",
    "help_text": (
        "📖 *Маълумотнома оид ба фармонҳои бот:*\n\n"
        "💬 *Илова кардани амалиёт:* Танҳо паёмро дар шакли озод фиристед, масалан: `себ 10 см` ё `маош 500$`.\n\n"
        "📌 *Фармонҳо:* \n"
        "• `/add <матн>` — илова кардани аниқи амалиёт\n"
        "• `/today` — ҳисобот барои имрӯз\n"
        "• `/week` — ҳисоботи ҳафтаина\n"
        "• `/month` — ҳисоботи моҳона бо график\n"
        "• `/report DD.MM.YYYY DD.MM.YYYY` — ҳисобот барои давра\n"
        "• `/export` — боркашии амалиётҳо ба Excel\n"
        "• `/categories` — идоракунии категорияҳо\n"
        "• `/addcategory <ном> <expense|income>` — илова кардани категория\n"
        "• `/setbudget <категория> <маблағ> <асъор>` — танзими буҷети моҳона\n"
        "• `/currency` — тағйири асъори асосӣ\n"
        "• `/rates` — қурби ҷории асъор\n"
        "• `/recurring` — рӯйхати пардохтҳои мунтазам\n"
        "• `/undo` — бекор кардани амалиёти охирин\n"
        "• `/addrecurring <категория> <маблағ> <асъор> <daily|weekly|monthly> <шарҳ>`\n"
        "• `/language` — интихоби забони интерфейс"
    ),

    # Main menu buttons
    "btn_today": "📊 Имрӯз",
    "btn_month": "📅 Ин моҳ",
    "btn_rates": "📈 Қурби асъор",
    "btn_categories": "📂 Категорияҳо",
    "btn_currency": "⚙️ Асъор",
    "btn_recurring": "🔄 Мунтазам",
    "btn_language": "🌐 Забон",

    # Language selection
    "lang_choose_title": "🌐 *Забони интерфейсро интихоб кунед / Выберите язык / Interfeys tilini tanlang / Select language:*",
    "lang_changed": "✅ Забони интерфейс ба *Тоҷикӣ* тағйир дода шуд!",

    # Currency selection
    "curr_current": "⚙️ Асъори асосии ҷории шумо: *{currency}*\n\nАсъори навро аз рӯйхати зер интихоб кунед:",
    "curr_changed": "✅ Асъори асосии шумо ба *{currency}* тағйир дода шуд!",
    "rates_title": "📈 *Қурби ҷории асъор (БМТ / Frankfurter):*\n\n🇺🇸 `1 USD` = `{usd:.4f} TJS`\n🇷🇺 `1 RUB` = `{rub:.4f} TJS`\n🇹🇯 `1 TJS` = `1.0000 TJS`\n\nҲамаи ҳисоботҳо бо қурби замони амалиёт ҳисоб карда мешаванд.",

    # Transactions & Parsing
    "tx_added_income": "🟢 *Даромад илова шуд!*",
    "tx_added_expense": "🔴 *Хароҷот илова шуд!*",
    "tx_amount_label": "💵 Маблағ: `{amount} {currency}` (~`{amount_base} {base_currency}`{rate_msg})",
    "tx_category_label": "🏷 Категория: {icon} {category}",
    "tx_comment_label": "📝 Шарҳ: {comment}",
    "parse_error_amount": "🤔 Маблағ дар паёми шумо муайян нашуд.\n\nКӯшиш кунед паёмро ин тавр нависед:\n• `себ 10 см`\n• `такси 25 руб`\n• `маош 500$`",
    "parse_confirm_category": "❓ Маблағи муайяншуда: `{amount} {currency}`.\nКатегорияро барои амалиёт интихоб кунед:",
    "cmd_add_usage": "Лутфан матни амалиётро баъди фармони /add ворид кунед, масалан:\n`/add ош 25 сомонӣ`",
    "btn_undo": "↩️ Бекор кардан",
    "btn_undo_confirm": "Бале, бекор кардан",
    "btn_undo_cancel": "Бекоркунӣ",
    "undo_transaction_details": "{icon} {amount} {currency}, категория: {category}",
    "undo_unknown_category": "Бе категория",
    "undo_confirm_prompt": "Ин амалиёт бекор карда шавад: {details}?",
    "undo_done": "❌ Амалиёт бекор карда шуд",
    "undo_kept": "Амалиёт бетағйир монд.",
    "undo_nothing": "Барои бекор кардан амалиёт ёфт нашуд.",
    "undo_expired": "Ин амалиёт барои бекор кардан хеле кӯҳна аст. Вақти бекоркунӣ гузаштааст.",
    "undo_unavailable": "Ин амалиёт аллакай бекор шудааст ё дастрас нест.",

    # Budgets
    "budget_exceeded": "⚠️ *ДИҚҚАТ! БУҶЕТ ЗИЁД ШУД!*\nКатегория: {icon} {category}\nСарф шуд: `{spent:.2f} {currency}` аз `{limit:.2f} {currency}` ({percent:.1f}%)",
    "budget_warning": "⚡ *Огоҳӣ оид ба буҷет ({percent:.1f}%)\nКатегория: {icon} {category}\nСарф шуд: `{spent:.2f} {currency}` аз меъёри `{limit:.2f} {currency}`",
    "budget_set_success": "🎯 Меъёри моҳона барои категорияи *{category}* гузошта шуд:\nМеъёр: `{limit} {currency}`\nОгоҳӣ ҳангоми 80% ва 100% сарф шудан фиристода мешавад.",
    "budget_set_usage": "⚠️ Шакли фармон:\n`/setbudget <категория> <маблағ> <асъор>`\nМасалан: `/setbudget Хӯрок 1500 TJS`",
    "budget_cat_not_found": "⚠️ Категорияи '{category}' ёфт нашуд. Рӯйхатро дар /categories санҷед.",
    "budget_invalid_amount": "⚠️ Маблағ бояд адад бошад.",
    "budget_invalid_currency": "⚠️ Асъор бояд TJS, RUB ё USD бошад.",

    # Reports
    "report_no_data": "📊 *Ҳисобот барои давра ({period})*\n\nДар давраи интихобшуда амалиёт ёфт нашуд.",
    "report_header": "📊 *Ҳисобот барои {period}*",
    "report_base_curr": "💰 *Асъори асосӣ:* {currency}",
    "report_total_expense": "🔻 *Ҷамъи хароҷот:* `{amount:.2f} {currency}`",
    "report_total_income": "🟢 *Ҷамъи даромад:* `{amount:.2f} {currency}`",
    "report_balance": "⚖️ *Баланси давра:* `{amount:.2f} {currency}`",
    "report_prev_comparison": "\n🔄 *Муқоиса бо давраи гузашта:* {sign}{pct:.1f}% ({prev_amount:.2f} {currency})",
    "report_by_categories": "📂 *Хароҷот аз рӯи категорияҳо:*",
    "report_chart_title": "Сохтори хароҷот ({currency})",
    "report_custom_usage": "⚠️ Шакли фармон:\n`/report DD.MM.YYYY DD.MM.YYYY`\nМасалан: `/report 01.09.2026 07.09.2026`",
    "report_date_format_error": "⚠️ Формати сана нодуруст аст. DD.MM.YYYY истифода баред, масалан: `01.09.2026`",
    "export_caption": "📂 *Боркашии амалиётҳои шумо ба Excel*",

    # Categories
    "cat_list_header": "📂 *Рӯйхати категорияҳои мавҷуда:*\n\n🔴 *Хароҷот:*\n{expenses}\n\n🟢 *Даромад:*\n{incomes}\n\n➕ *Илова кардани категорияи худ:*\n`/addcategory <ном> <expense|income>`\nМасалан: `/addcategory Обунаҳо expense`",
    "cat_add_usage": "⚠️ Шакли фармон нодуруст аст.\nИстифода: `/addcategory <ном> <expense|income>`\nМасалан: `/addcategory Фриланс income`",
    "cat_type_error": "⚠️ Навъи категория бояд `expense` (хароҷот) ё `income` (даромад) бошад.",
    "cat_added_success": "✅ Категорияи *{name}* ({type_title}) муваффақона илова шуд!",

    # Recurring
    "rec_empty": "🔄 *Шумо пардохтҳои мунтазами фаъол надоред.*\n\nБарои илова кардани пардохти мунтазам истифода баред:\n`/addrecurring <категория> <маблағ> <асъор> <daily|weekly|monthly> [шарҳ]`\nМасалан: `/addrecurring Манзил 500 USD monthly Иҷораи хона`",
    "rec_header": "🔄 *Пардохтҳои мунтазами шумо:*\n",
    "rec_add_usage": "⚠️ Шакли фармон:\n`/addrecurring <категория> <маблағ> <асъор> <daily|weekly|monthly> [шарҳ]`\nМасалан: `/addrecurring Манзил 500 USD monthly Иҷораи хона`",
    "rec_freq_error": "⚠️ Даврият бояд `daily`, `weekly` ё `monthly` бошад.",
    "rec_added_success": "✅ *Пардохти мунтазам сохта шуд!*\n\n🏷 Категория: {icon} {category}\n💵 Маблағ: `{amount} {currency}`\n🔄 Даврият: {frequency}\n🕒 Пардохти навбатӣ: {next_run}",
    "rec_executed_notify": "🔄 *Пардохти мунтазам иҷро шуд!*\n\n💰 Маблағ: `{amount} {currency}`\n📝 Шарҳ: {comment}",
    "evening_reminder": "🔔 *Огоҳии бегоҳирӯзӣ*\n\nШумо хароҷоти имрӯзро ворид накардаед. Навиштани онро фаромӯш накунед! 📝",
}
