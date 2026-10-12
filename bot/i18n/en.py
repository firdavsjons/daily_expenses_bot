TRANSLATIONS = {
    # General / Commands
    "start_welcome": (
        "👋 Hello, *{first_name}*!\n\n"
        "I am a smart bot for tracking personal income and expenses 💰\n\n"
        "You can simply send me messages in natural language, for example:\n"
        "• _bought apple for 10 somoni_\n"
        "• _taxi 25 rub_\n"
        "• _lunch 15$_\n"
        "• _salary 500 dollar_\n\n"
        "Your default base currency is: *{base_currency}*.\n"
        "Select your preferred base currency below:"
    ),
    "menu_open": "Main menu opened:",
    "help_text": (
        "📖 *Bot Commands Help:*\n\n"
        "💬 *Add Transactions:* Just send a message in free text, e.g.: `apple 10 sm` or `salary 500$`.\n\n"
        "📌 *Commands:* \n"
        "• `/add <text>` — add transaction explicitly\n"
        "• `/today` — today's report\n"
        "• `/week` — weekly report\n"
        "• `/month` — monthly report with pie chart\n"
        "• `/report DD.MM.YYYY DD.MM.YYYY` — custom period report\n"
        "• `/export` — export transactions to Excel\n"
        "• `/categories` — manage categories\n"
        "• `/addcategory <name> <expense|income>` — add custom category\n"
        "• `/setbudget <category> <amount> <currency>` — set monthly limit\n"
        "• `/currency` — change base currency\n"
        "• `/rates` — current exchange rates\n"
        "• `/recurring` — list recurring payments\n"
        "• `/undo` — undo the latest transaction\n"
        "• `/addrecurring <category> <amount> <currency> <daily|weekly|monthly> <comment>`\n"
        "• `/language` — choose interface language"
    ),

    # Main menu buttons
    "btn_today": "📊 Today",
    "btn_month": "📅 This Month",
    "btn_rates": "📈 Exchange Rates",
    "btn_categories": "📂 Categories",
    "btn_currency": "⚙️ Currency",
    "btn_recurring": "🔄 Recurring",
    "btn_language": "🌐 Language",

    # Language selection
    "lang_choose_title": "🌐 *Select interface language / Выберите язык / Interfeys tilini tanlang / Забони интерфейсро интихоб кунед:*",
    "lang_changed": "✅ Interface language changed to *English*!",

    # Currency selection
    "curr_current": "⚙️ Your current base currency is: *{currency}*\n\nSelect a new currency from the list below:",
    "curr_changed": "✅ Your base currency has been changed to *{currency}*!",
    "rates_title": "📈 *Current Exchange Rates (NBT / Frankfurter):*\n\n🇺🇸 `1 USD` = `{usd:.4f} TJS`\n🇷🇺 `1 RUB` = `{rub:.4f} TJS`\n🇹🇯 `1 TJS` = `1.0000 TJS`\n\nAll reports are calculated using rates at transaction time.",

    # Transactions & Parsing
    "tx_added_income": "🟢 *Income added!*",
    "tx_added_expense": "🔴 *Expense added!*",
    "tx_amount_label": "💵 Amount: `{amount} {currency}` (~`{amount_base} {base_currency}`{rate_msg})",
    "tx_category_label": "🏷 Category: {icon} {category}",
    "tx_comment_label": "📝 Comment: {comment}",
    "parse_error_amount": "🤔 Could not recognize an amount in your message.\n\nTry writing like this:\n• `apple 10 sm`\n• `taxi 25 rub`\n• `salary 500$`",
    "parse_confirm_category": "❓ Recognized amount: `{amount} {currency}`.\nSelect a category for this transaction:",
    "cmd_add_usage": "Please specify transaction text after /add command, e.g.:\n`/add lunch 25 somoni`",
    "btn_undo": "↩️ Undo",
    "btn_undo_confirm": "Yes, undo",
    "btn_undo_cancel": "Cancel",
    "undo_transaction_details": "{icon} {amount} {currency}, category {category}",
    "undo_unknown_category": "Uncategorized",
    "undo_confirm_prompt": "Undo this transaction: {details}?",
    "undo_done": "❌ Transaction undone",
    "undo_kept": "Transaction kept unchanged.",
    "undo_nothing": "No transactions found to undo.",
    "undo_expired": "This transaction is too old to undo. The undo window has expired.",
    "undo_unavailable": "This transaction was already undone or is unavailable.",

    # Budgets
    "budget_exceeded": "⚠️ *WARNING! BUDGET EXCEEDED!*\nCategory: {icon} {category}\nSpent: `{spent:.2f} {currency}` of `{limit:.2f} {currency}` ({percent:.1f}%)",
    "budget_warning": "⚡ *Budget Alert ({percent:.1f}%)\nCategory: {icon} {category}\nSpent: `{spent:.2f} {currency}` of limit `{limit:.2f} {currency}`",
    "budget_set_success": "🎯 Monthly budget limit set for *{category}*:\nLimit: `{limit} {currency}`\nNotifications will be sent at 80% and 100% threshold.",
    "budget_set_usage": "⚠️ Command format:\n`/setbudget <category> <amount> <currency>`\nExample: `/setbudget Food 1500 TJS`",
    "budget_cat_not_found": "⚠️ Category '{category}' not found. Check /categories list.",
    "budget_invalid_amount": "⚠️ Amount must be a number.",
    "budget_invalid_currency": "⚠️ Currency must be TJS, RUB or USD.",

    # Reports
    "report_no_data": "📊 *Period Report ({period})*\n\nNo transactions found for the selected period.",
    "report_header": "📊 *Report for {period}*",
    "report_base_curr": "💰 *Base Currency:* {currency}",
    "report_total_expense": "🔻 *Total Expenses:* `{amount:.2f} {currency}`",
    "report_total_income": "🟢 *Total Income:* `{amount:.2f} {currency}`",
    "report_balance": "⚖️ *Period Balance:* `{amount:.2f} {currency}`",
    "report_prev_comparison": "\n🔄 *Previous Period Comparison:* {sign}{pct:.1f}% ({prev_amount:.2f} {currency})",
    "report_by_categories": "📂 *Expenses by Category:*",
    "report_chart_title": "Expense Breakdown ({currency})",
    "report_custom_usage": "⚠️ Command format:\n`/report DD.MM.YYYY DD.MM.YYYY`\nExample: `/report 01.09.2026 07.09.2026`",
    "report_date_format_error": "⚠️ Invalid date format. Use DD.MM.YYYY, e.g.: `01.09.2026`",
    "export_caption": "📂 *Exporting your transactions to Excel*",

    # Categories
    "cat_list_header": "📂 *List of Available Categories:*\n\n🔴 *Expenses:*\n{expenses}\n\n🟢 *Income:*\n{incomes}\n\n➕ *Add Custom Category:*\n`/addcategory <name> <expense|income>`\nExample: `/addcategory Subscriptions expense`",
    "cat_add_usage": "⚠️ Invalid command format.\nUsage: `/addcategory <name> <expense|income>`\nExample: `/addcategory Freelance income`",
    "cat_type_error": "⚠️ Category type must be `expense` or `income`.",
    "cat_added_success": "✅ Category *{name}* ({type_title}) successfully added!",

    # Recurring
    "rec_empty": "🔄 *You have no active recurring payments.*\n\nTo add a recurring payment, use:\n`/addrecurring <category> <amount> <currency> <daily|weekly|monthly> [comment]`\nExample: `/addrecurring Housing 500 USD monthly Rent apartment`",
    "rec_header": "🔄 *Your Recurring Payments:*\n",
    "rec_add_usage": "⚠️ Command format:\n`/addrecurring <category> <amount> <currency> <daily|weekly|monthly> [comment]`\nExample: `/addrecurring Housing 500 USD monthly Rent apartment`",
    "rec_freq_error": "⚠️ Frequency must be `daily`, `weekly` or `monthly`.",
    "rec_added_success": "✅ *Recurring payment created!*\n\n🏷 Category: {icon} {category}\n💵 Amount: `{amount} {currency}`\n🔄 Frequency: {frequency}\n🕒 Next Run: {next_run}",
    "rec_executed_notify": "🔄 *Recurring payment executed!*\n\n💰 Amount: `{amount} {currency}`\n📝 Comment: {comment}",
    "evening_reminder": "🔔 *Evening Reminder*\n\nYou haven't logged any expenses today. Don't forget to record them! 📝",
}
