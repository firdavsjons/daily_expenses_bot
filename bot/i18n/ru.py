TRANSLATIONS = {
    # General / Commands
    "start_welcome": (
        "👋 Здравствуйте, *{first_name}*!\n\n"
        "Я умный бот для учёта личных доходов и расходов 💰\n\n"
        "Вы можете просто писать мне фразы на естественном языке, например:\n"
        "• _купил яблоко за 10 сомони_\n"
        "• _такси 25 руб_\n"
        "• _обед 15$_\n"
        "• _зарплата 500 доллар_\n\n"
        "По умолчанию ваша базовая валюта: *{base_currency}*.\n"
        "Выберите базовую валюту ниже, если хотите изменить её:"
    ),
    "menu_open": "Главное меню открыто:",
    "help_text": (
        "📖 *Справка по командам бота:*\n\n"
        "💬 *Добавление операций:* Просто отправьте сообщение в свободном формате, например: `яблоко 10 см` или `зарплата 500$`.\n\n"
        "📌 *Команды:* \n"
        "• `/add <текст>` — явное добавление операции\n"
        "• `/today` — отчёт за сегодня\n"
        "• `/week` — отчёт за неделю\n"
        "• `/month` — отчёт за месяц с графиком\n"
        "• `/report DD.MM.YYYY DD.MM.YYYY` — отчёт за период\n"
        "• `/export` — выгрузить транзакции в Excel\n"
        "• `/categories` — управление категориями\n"
        "• `/addcategory <название> <expense|income>` — добавить категорию\n"
        "• `/setbudget <категория> <сумма> <валюта>` — установить месячный бюджет\n"
        "• `/currency` — смена базовой валюты\n"
        "• `/rates` — текущие курсы валют\n"
        "• `/recurring` — список регулярных платежей\n"
        "• `/undo` — отменить последнюю операцию\n"
        "• `/addrecurring <категория> <сумма> <валюта> <daily|weekly|monthly> <коммент>`\n"
        "• `/language` — выбор языка интерфейса"
    ),

    # Main menu buttons
    "btn_today": "📊 Сегодня",
    "btn_month": "📅 Месяц",
    "btn_rates": "📈 Курсы валют",
    "btn_categories": "📂 Категории",
    "btn_currency": "⚙️ Валюта",
    "btn_recurring": "🔄 Регулярные",
    "btn_language": "🌐 Язык",

    # Language selection
    "lang_choose_title": "🌐 *Выберите язык интерфейса / Интерфейс тилини танланг / Забони интерфейсро интихоб кунед / Select language:*",
    "lang_changed": "✅ Язык интерфейса изменён на *Русский*!",

    # Currency selection
    "curr_current": "⚙️ Ваша текущая базовая валюта: *{currency}*\n\nВыберите новую валюту из списка ниже:",
    "curr_changed": "✅ Ваша базовая валюта изменена на *{currency}*!",
    "rates_title": "📈 *Текущие курсы валют (НБТ / Frankfurter):*\n\n🇺🇸 `1 USD` = `{usd:.4f} TJS`\n🇷🇺 `1 RUB` = `{rub:.4f} TJS`\n🇹🇯 `1 TJS` = `1.0000 TJS`\n\nВсе отчёты пересчитываются по курсам на момент операции.",

    # Transactions & Parsing
    "tx_added_income": "🟢 *Доход добавлен!*",
    "tx_added_expense": "🔴 *Расход добавлен!*",
    "tx_amount_label": "💵 Сумма: `{amount} {currency}` (~`{amount_base} {base_currency}`{rate_msg})",
    "tx_category_label": "🏷 Категория: {icon} {category}",
    "tx_comment_label": "📝 Комментарий: {comment}",
    "parse_error_amount": "🤔 Не удалось распознать сумму в вашем сообщении.\n\nПопробуйте написать, например:\n• `яблоко 10 см`\n• `такси 25 руб`\n• `зарплата 500$`",
    "parse_confirm_category": "❓ Распознана сумма: `{amount} {currency}`.\nВыберите категорию для операции:",
    "cmd_add_usage": "Пожалуйста, укажите текст операции после команды /add, например:\n`/add обед 25 сомони`",
    "btn_undo": "↩️ Отменить",
    "btn_undo_confirm": "Да, отменить",
    "btn_undo_cancel": "Отмена",
    "undo_transaction_details": "{icon} {amount} {currency}, категория {category}",
    "undo_unknown_category": "Без категории",
    "undo_confirm_prompt": "Отменить эту операцию: {details}?",
    "undo_done": "❌ Операция отменена",
    "undo_kept": "Операция оставлена без изменений.",
    "undo_nothing": "Операций для отмены не найдено.",
    "undo_expired": "Эта операция слишком старая для отмены. Время отмены истекло.",
    "undo_unavailable": "Эта операция уже отменена или недоступна.",

    # Budgets
    "budget_exceeded": "⚠️ *ВНИМАНИЕ! БЮДЖЕТ ПРЕВЫШЕН!*\nКатегория: {icon} {category}\nИзрасходовано: `{spent:.2f} {currency}` из `{limit:.2f} {currency}` ({percent:.1f}%)",
    "budget_warning": "⚡ *Предупреждение по бюджету ({percent:.1f}%)\nКатегория: {icon} {category}\nИзрасходовано: `{spent:.2f} {currency}` из лимита `{limit:.2f} {currency}`",
    "budget_set_success": "🎯 Установлен месячный лимит для категории *{category}*:\nЛимит: `{limit} {currency}`\nУведомления отправятся при 80% и 100% расхода.",
    "budget_set_usage": "⚠️ Формат команды:\n`/setbudget <категория> <сумма> <валюта>`\nПример: `/setbudget Еда 1500 TJS`",
    "budget_cat_not_found": "⚠️ Категория '{category}' не найдена. Проверьте список в /categories.",
    "budget_invalid_amount": "⚠️ Сумма должна быть числом.",
    "budget_invalid_currency": "⚠️ Валюта должна быть TJS, RUB или USD.",

    # Reports
    "report_no_data": "📊 *Отчёт за период ({period})*\n\nЗа выбранный период операций не найдено.",
    "report_header": "📊 *Отчёт за {period}*",
    "report_base_curr": "💰 *Базовая валюта:* {currency}",
    "report_total_expense": "🔻 *Всего расходов:* `{amount:.2f} {currency}`",
    "report_total_income": "🟢 *Всего доходов:* `{amount:.2f} {currency}`",
    "report_balance": "⚖️ *Баланс периода:* `{amount:.2f} {currency}`",
    "report_prev_comparison": "\n🔄 *Сравнение с прошлым периодом:* {sign}{pct:.1f}% ({prev_amount:.2f} {currency})",
    "report_by_categories": "📂 *Расходы по категориям:*",
    "report_chart_title": "Структура расходов ({currency})",
    "report_custom_usage": "⚠️ Формат команды:\n`/report DD.MM.YYYY DD.MM.YYYY`\nПример: `/report 01.09.2026 07.09.2026`",
    "report_date_format_error": "⚠️ Неверный формат даты. Используйте DD.MM.YYYY, например: `01.09.2026`",
    "export_caption": "📂 *Выгрузка ваших транзакций в Excel*",

    # Categories
    "cat_list_header": "📂 *Список доступных категорий:*\n\n🔴 *Расходы:*\n{expenses}\n\n🟢 *Доходы:*\n{incomes}\n\n➕ *Добавить свою категорию:*\n`/addcategory <название> <expense|income>`\nПример: `/addcategory Подписки expense`",
    "cat_add_usage": "⚠️ Неверный формат команды.\nИспользуйте: `/addcategory <название> <expense|income>`\nПример: `/addcategory Фриланс income`",
    "cat_type_error": "⚠️ Тип категории должен быть `expense` (расход) или `income` (доход).",
    "cat_added_success": "✅ Категория *{name}* ({type_title}) успешно добавлена!",

    # Recurring
    "rec_empty": "🔄 *У вас нет активных регулярных платежей.*\n\nЧтобы добавить регулярный платёж, используйте:\n`/addrecurring <категория> <сумма> <валюта> <daily|weekly|monthly> [коммент]`\nПример: `/addrecurring Жильё 500 USD monthly Аренда квартиры`",
    "rec_header": "🔄 *Ваши регулярные платежи:*\n",
    "rec_add_usage": "⚠️ Формат команды:\n`/addrecurring <категория> <сумма> <валюта> <daily|weekly|monthly> [комментарий]`\nПример: `/addrecurring Жильё 500 USD monthly Аренда квартиры`",
    "rec_freq_error": "⚠️ Периодичность должна быть `daily`, `weekly` или `monthly`.",
    "rec_added_success": "✅ *Регулярный платёж успешно создан!*\n\n🏷 Категория: {icon} {category}\n💵 Сумма: `{amount} {currency}`\n🔄 Частота: {frequency}\n🕒 Следующее списание: {next_run}",
    "rec_executed_notify": "🔄 *Исполнен регулярный платёж!*\n\n💰 Сумма: `{amount} {currency}`\n📝 Комментарий: {comment}",
    "evening_reminder": "🔔 *Вечернее напоминание*\n\nВы ещё не внесли расходы за сегодня. Не забудьте записать свои траты! 📝",
}
