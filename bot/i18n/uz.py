TRANSLATIONS = {
    # General / Commands
    "start_welcome": (
        "👋 Assalomu alaykum, *{first_name}*!\n\n"
        "Men shaxsiy daromad va xarajatlarni hisobga oluvchi aqlli botman 💰\n\n"
        "Menga oddiy tilda xabarlar yuborishingiz mumkin, masalan:\n"
        "• _10 somoniga olma oldim_\n"
        "• _taksi 25 rub_\n"
        "• _tushlik 15$_\n"
        "• _oylik 500 dollar_\n\n"
        "Standart asosiy valyutangiz: *{base_currency}*.\n"
        "O'zgartirish uchun quyidagi valyutani tanlang:"
    ),
    "menu_open": "Asosiy menyu ochildi:",
    "help_text": (
        "📖 *Bot buyruqlari bo'yicha ma'lumot:*\n\n"
        "💬 *Amallarni qo'shish:* Shunchaki erkin formatda xabar yuboring, masalan: `olma 10 sm` yoki `oylik 500$`.\n\n"
        "📌 *Buyruqlar:* \n"
        "• `/add <matn>` — amalni aniq qo'shish\n"
        "• `/today` — bugungi hisobot\n"
        "• `/week` — haftalik hisobot\n"
        "• `/month` — grafikli oylik hisobot\n"
        "• `/report DD.MM.YYYY DD.MM.YYYY` — davr bo'yicha hisobot\n"
        "• `/export` — tranzaksiyalarni Excel-ga yuklash\n"
        "• `/categories` — kategoriyalarni boshqarish\n"
        "• `/addcategory <nomi> <expense|income>` — kategoriya qo'shish\n"
        "• `/setbudget <kategoriya> <summa> <valyuta>` — oylik me'yor belgilash\n"
        "• `/currency` — asosiy valyutani o'zgartirish\n"
        "• `/rates` — amaldagi valyuta kurslari\n"
        "• `/recurring` — muntazam to'lovlar ro'yxati\n"
        "• `/undo` — oxirgi amalni bekor qilish\n"
        "• `/addrecurring <kategoriya> <summa> <valyuta> <daily|weekly|monthly> <izoh>`\n"
        "• `/language` — interfeys tilini tanlash"
    ),

    # Main menu buttons
    "btn_today": "📊 Bugun",
    "btn_month": "📅 Shu oy",
    "btn_rates": "📈 Valyuta kurslari",
    "btn_categories": "📂 Kategoriyalar",
    "btn_currency": "⚙️ Valyuta",
    "btn_recurring": "🔄 Muntazam",
    "btn_language": "🌐 Til",

    # Language selection
    "lang_choose_title": "🌐 *Interfeys tilini tanlang / Выберите язык / Забони интерфейсро интихоб кунед / Select language:*",
    "lang_changed": "✅ Interfeys tili *O'zbekcha*ga o'zgartirildi!",

    # Currency selection
    "curr_current": "⚙️ Hozirgi asosiy valyutangiz: *{currency}*\n\nQuyidagi ro'yxatdan yangi valyutani tanlang:",
    "curr_changed": "✅ Asosiy valyutangiz *{currency}* ga o'zgartirildi!",
    "rates_title": "📈 *Amaldagi valyuta kurslari (NBT / Frankfurter):*\n\n🇺🇸 `1 USD` = `{usd:.4f} TJS`\n🇷🇺 `1 RUB` = `{rub:.4f} TJS`\n🇹🇯 `1 TJS` = `1.0000 TJS`\n\nBarcha hisobotlar amal bajarilgan vaqtdagi kurs bo'yicha hisoblanadi.",

    # Transactions & Parsing
    "tx_added_income": "🟢 *Daromad qo'shildi!*",
    "tx_added_expense": "🔴 *Xarajat qo me'yori qo'shildi!*",
    "tx_amount_label": "💵 Summa: `{amount} {currency}` (~`{amount_base} {base_currency}`{rate_msg})",
    "tx_category_label": "🏷 Kategoriya: {icon} {category}",
    "tx_comment_label": "📝 Izoh: {comment}",
    "parse_error_amount": "🤔 Xabaringizda summa aniqlanmadi.\n\nMasalan, quyidagicha yozib ko'ring:\n• `olma 10 sm`\n• `taksi 25 rub`\n• `oylik 500$`",
    "parse_confirm_category": "❓ Summa aniqlandi: `{amount} {currency}`.\nAmal uchun kategoriyani tanlang:",
    "cmd_add_usage": "Iltimos, /add buyrug'idan so'ng amal matnini kiriting, masalan:\n`/add tushlik 25 somoni`",
    "btn_undo": "↩️ Bekor qilish",
    "btn_undo_confirm": "Ha, bekor qilish",
    "btn_undo_cancel": "Bekor qilish",
    "undo_transaction_details": "{icon} {amount} {currency}, kategoriya: {category}",
    "undo_unknown_category": "Kategoriyasiz",
    "undo_confirm_prompt": "Bu amal bekor qilinsinmi: {details}?",
    "undo_done": "❌ Amal bekor qilindi",
    "undo_kept": "Amal o'zgarishsiz qoldirildi.",
    "undo_nothing": "Bekor qilish uchun amallar topilmadi.",
    "undo_expired": "Bu amalni bekor qilish uchun juda eski. Bekor qilish vaqti tugagan.",
    "undo_unavailable": "Bu amal allaqachon bekor qilingan yoki mavjud emas.",

    # Budgets
    "budget_exceeded": "⚠️ *DIQQAT! BYUDJET ME'YORI OSHDI!*\nKategoriya: {icon} {category}\nSarflandi: `{spent:.2f} {currency}` / `{limit:.2f} {currency}` ({percent:.1f}%)",
    "budget_warning": "⚡ *Byudjet bo'yicha ogohlantirish ({percent:.1f}%)\nKategoriya: {icon} {category}\nSarflandi: `{spent:.2f} {currency}` / me'yor `{limit:.2f} {currency}`",
    "budget_set_success": "🎯 *{category}* kategoriyasi uchun oylik me me'yor belgilandi:\nMe'yor: `{limit} {currency}`\nOgohlantirish 80% va 100% sarflanganda yuboriladi.",
    "budget_set_usage": "⚠️ Buyruq formati:\n`/setbudget <kategoriya> <summa> <valyuta>`\nMasalan: `/setbudget Ovqat 1500 TJS`",
    "budget_cat_not_found": "⚠️ '{category}' kategoriyasi topilmadi. /categories ro'yxatini tekshiring.",
    "budget_invalid_amount": "⚠️ Summa son bo'lishi kerak.",
    "budget_invalid_currency": "⚠️ Valyuta TJS, RUB yoki USD bo'lishi kerak.",

    # Reports
    "report_no_data": "📊 *Davr bo'yicha hisobot ({period})*\n\nTanlangan davrda amallar topilmadi.",
    "report_header": "📊 *{period} bo'yicha hisobot*",
    "report_base_curr": "💰 *Asosiy valyuta:* {currency}",
    "report_total_expense": "🔻 *Jami xarajatlar:* `{amount:.2f} {currency}`",
    "report_total_income": "🟢 *Jami daromadlar:* `{amount:.2f} {currency}`",
    "report_balance": "⚖️ *Davr balansi:* `{amount:.2f} {currency}`",
    "report_prev_comparison": "\n🔄 *O'tgan davr bilan taqqoslash:* {sign}{pct:.1f}% ({prev_amount:.2f} {currency})",
    "report_by_categories": "📂 *Kategoriyalar bo'yicha xarajatlar:*",
    "report_chart_title": "Xarajatlar tuzilmasi ({currency})",
    "report_custom_usage": "⚠️ Buyruq formati:\n`/report DD.MM.YYYY DD.MM.YYYY`\nMasalan: `/report 01.09.2026 07.09.2026`",
    "report_date_format_error": "⚠️ Sana formati noto'g'ri. DD.MM.YYYY ishlating, masalan: `01.09.2026`",
    "export_caption": "📂 *Tranzaksiyalaringizni Excel-ga yuklash*",

    # Categories
    "cat_list_header": "📂 *Mavjud kategoriyalar ro'yxati:*\n\n🔴 *Xarajatlar:*\n{expenses}\n\n🟢 *Daromadlar:*\n{incomes}\n\n➕ *O'z kategoriyangizni qo'shing:*\n`/addcategory <nomi> <expense|income>`\nMasalan: `/addcategory Obunalar expense`",
    "cat_add_usage": "⚠️ Buyruq formati noto'g me'yoriy.\nIshlatish: `/addcategory <nomi> <expense|income>`\nMasalan: `/addcategory Frilans income`",
    "cat_type_error": "⚠️ Kategoriya turi `expense` (xarajat) yoki `income` (daromad) bo'lishi kerak.",
    "cat_added_success": "✅ *{name}* kategoriyasi ({type_title}) muvaffaqiyatli qo'shildi!",

    # Recurring
    "rec_empty": "🔄 *Sizda faol muntazam to'lovlar yo'q.*\n\nMuntazam to'lov qo'shish uchun ishlating:\n`/addrecurring <kategoriya> <summa> <valyuta> <daily|weekly|monthly> [izoh]`\nMasalan: `/addrecurring Uy 500 USD monthly Uy ijarasi`",
    "rec_header": "🔄 *Sizning muntazam to'lovlaringiz:*\n",
    "rec_add_usage": "⚠️ Buyruq formati:\n`/addrecurring <kategoriya> <summa> <valyuta> <daily|weekly|monthly> [izoh]`\nMasalan: `/addrecurring Uy 500 USD monthly Uy ijarasi`",
    "rec_freq_error": "⚠️ Davriylik `daily`, `weekly` yoki `monthly` bo'lishi kerak.",
    "rec_added_success": "✅ *Muntazam to'lov yaratildi!*\n\n🏷 Kategoriya: {icon} {category}\n💵 Summa: `{amount} {currency}`\n🔄 Takrorlanish: {frequency}\n🕒 Keyingi to'lov: {next_run}",
    "rec_executed_notify": "🔄 *Muntazam to'lov bajarildi!*\n\n💰 Summa: `{amount} {currency}`\n📝 Izoh: {comment}",
    "evening_reminder": "🔔 *Kechki eslatma*\n\nBugungi xarajatlaringizni kiritmadingiz. Yozib qo'yishni unutmang! 📝",
}
