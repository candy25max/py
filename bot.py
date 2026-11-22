import asyncio
import base64
import json
import os
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "9184524998:AAHFBLU85WWV-3ArSduiCp9CdyERwWYjvgE")
URL_WEBAPP = os.getenv("URL_WEBAPP", "https://glimup.vercel.app")
ADMIN_IDS: set[int] = {7828950337}
DATA_FILE = "bot_data.json"

DEFAULT_CASES: dict[str, dict] = {
    "dragon": {"name": "Дракон", "price": 500, "reward_min": 50, "reward_max": 1200},
    "taco": {"name": "Тако", "price": 209, "reward_min": 20, "reward_max": 500},
    "nubini": {"name": "Нубини", "price": 19, "reward_min": 5, "reward_max": 60},
    "blok": {"name": "Блок", "price": 259, "reward_min": 30, "reward_max": 700},
}

DEFAULT_PROMOS: dict[str, int] = {
    "GLIMUP100": 100,
    "START50": 50,
}

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "choose_lang": "Выберите ваш язык / Choose your language:",
        "lang_selected": "Язык выбран: {lang_name}. Баланс: {bal} ⭐",
        "lang_name": "Русский",
        "btn_open": "Открыть GlimUp",
        "btn_topup": "Пополнить",
        "btn_promo": "Промокод",
        "btn_change_lang": "Сменить язык",
        "btn_admin": "🛠 Админ-панель",
        "ask_promo": "Введите промокод:",
        "promo_not_found": "❌ Промокод не найден или недействителен.",
        "promo_already_used": "⚠️ Вы уже активировали этот промокод.",
        "promo_activated": "✅ Промокод <b>{code}</b> активирован! Начислено: <b>+{reward} ⭐</b>\nТекущий баланс: <b>{bal} ⭐</b>",
        "ask_topup_amount": "Выберите, сколько звёзд хотите пополнить:",
        "btn_custom_amount": "✍️ Своя сумма",
        "ask_custom_amount": "Введите целое положительное число — сколько звёзд хотите пополнить (например: 25):",
        "invalid_positive_int": "Введите целое положительное число больше 0, например: 25",
        "invoice_title": "Пополнение баланса",
        "invoice_desc": "Пополнение баланса на {stars} ⭐",
        "invoice_label": "{stars} звёзд",
        "payment_ok": "✅ Оплата подтверждена! Начислено <b>{stars} ⭐</b>.\nТекущий баланс: <b>{bal} ⭐</b>",
        "webapp_topup_default": "Выберите количество звёзд для пополнения:",
        "webapp_topup_needed": "Для открытия кейса не хватает <b>{needed} ⭐</b>. Выберите сумму пополнения:",
        "case_not_found": "❌ Кейс не найден.",
        "not_enough_stars": "❌ Не хватает <b>{missing} ⭐</b>!",
        "case_opened": "🎁 Вы открыли кейс <b>{name}</b> за <b>{price} ⭐</b>!\nВыпало: <b>{drop} ⭐</b>\nТекущий баланс: <b>{bal} ⭐</b>",
        "upgrade_success": "🎉 <b>УСПЕХ!</b> Получено <b>{target} ⭐</b>.\nБаланс: <b>{bal} ⭐</b>",
        "upgrade_fail": "💀 <b>НЕУДАЧА!</b> Потеряно <b>{source} ⭐</b>.\nБаланс: <b>{bal} ⭐</b>",
        "no_admin": "⛔ Нет доступа к админ-панели.",
        "admin_title": "🛠 <b>Админ-панель</b>\nВыберите действие:",
        "admin_btn_balance": "💰 Выдать / изменить баланс",
        "admin_btn_prices": "🎯 Изменить цену кейса",
        "admin_btn_promo": "🎟 Добавить промокод",
        "admin_btn_stats": "📊 Статистика бота",
        "admin_ask_balance": "Отправьте в формате: <code>USER_ID НОВЫЙ_БАЛАНС</code>\nНапример: <code>7828950337 500</code>",
        "admin_bad_balance": "Формат: <code>USER_ID BALANCE</code> (например: <code>7828950337 500</code>)",
        "admin_balance_ok": "✅ Баланс пользователя <code>{uid}</code> сохранён: <b>{bal} ⭐</b>",
        "admin_ask_case": "Выберите кейс, чтобы изменить его цену в звёздах:",
        "admin_ask_price": "Введите новую цену в звёздах для кейса <b>{name}</b>:",
        "admin_price_ok": "✅ Новая цена кейса <b>{name}</b> сохранена: <b>{price} ⭐</b>",
        "admin_ask_promo": "Отправьте в формате: <code>КОД ЗВЁЗДЫ</code>\nНапример: <code>BONUS200 200</code>",
        "admin_bad_promo": "Формат: <code>КОД ЗВЁЗДЫ</code> (например: <code>BONUS200 200</code>)",
        "admin_promo_ok": "✅ Промокод <b>{code}</b> на <b>{reward} ⭐</b> добавлен.",
        "admin_stats": "📊 <b>Статистика</b>\nПользователей в базе: <b>{users}</b>\nСуммарный баланс в боте: <b>{stars} ⭐</b>",
        "back": "⬅️ Назад",
    },
    "en": {
        "choose_lang": "Выберите ваш язык / Choose your language:",
        "lang_selected": "Language selected: {lang_name}. Balance: {bal} ⭐",
        "lang_name": "English",
        "btn_open": "Open GlimUp",
        "btn_topup": "Top up",
        "btn_promo": "Promo code",
        "btn_change_lang": "Change language",
        "btn_admin": "🛠 Admin panel",
        "ask_promo": "Enter promo code:",
        "promo_not_found": "❌ Promo code not found or invalid.",
        "promo_already_used": "⚠️ You have already activated this promo code.",
        "promo_activated": "✅ Promo code <b>{code}</b> activated! Credited: <b>+{reward} ⭐</b>\nCurrent balance: <b>{bal} ⭐</b>",
        "ask_topup_amount": "Choose how many Stars you want to top up:",
        "btn_custom_amount": "✍️ Custom amount",
        "ask_custom_amount": "Enter a positive integer — how many Stars to top up (e.g. 25):",
        "invalid_positive_int": "Enter a positive integer greater than 0, e.g.: 25",
        "invoice_title": "Balance Top Up",
        "invoice_desc": "Top up balance by {stars} ⭐",
        "invoice_label": "{stars} Stars",
        "payment_ok": "✅ Payment confirmed! Credited <b>{stars} ⭐</b>.\nCurrent balance: <b>{bal} ⭐</b>",
        "webapp_topup_default": "Choose how many Stars to top up:",
        "webapp_topup_needed": "You need <b>{needed} ⭐</b> more to open the case. Choose top-up amount:",
        "case_not_found": "❌ Case not found.",
        "not_enough_stars": "❌ Not enough <b>{missing} ⭐</b>!",
        "case_opened": "🎁 You opened case <b>{name}</b> for <b>{price} ⭐</b>!\nDropped: <b>{drop} ⭐</b>\nCurrent balance: <b>{bal} ⭐</b>",
        "upgrade_success": "🎉 <b>SUCCESS!</b> Received <b>{target} ⭐</b>.\nBalance: <b>{bal} ⭐</b>",
        "upgrade_fail": "💀 <b>FAILED!</b> Lost <b>{source} ⭐</b>.\nBalance: <b>{bal} ⭐</b>",
        "no_admin": "⛔ No access to admin panel.",
        "admin_title": "🛠 <b>Admin Panel</b>\nChoose an action:",
        "admin_btn_balance": "💰 Set / change balance",
        "admin_btn_prices": "🎯 Change case price",
        "admin_btn_promo": "🎟 Add promo code",
        "admin_btn_stats": "📊 Bot statistics",
        "admin_ask_balance": "Send in format: <code>USER_ID NEW_BALANCE</code>\nExample: <code>7828950337 500</code>",
        "admin_bad_balance": "Format: <code>USER_ID BALANCE</code> (example: <code>7828950337 500</code>)",
        "admin_balance_ok": "✅ User <code>{uid}</code> balance saved: <b>{bal} ⭐</b>",
        "admin_ask_case": "Choose a case to change its price in Stars:",
        "admin_ask_price": "Enter a new price in Stars for case <b>{name}</b>:",
        "admin_price_ok": "✅ New price for case <b>{name}</b> saved: <b>{price} ⭐</b>",
        "admin_ask_promo": "Send in format: <code>CODE STARS</code>\nExample: <code>BONUS200 200</code>",
        "admin_bad_promo": "Format: <code>CODE STARS</code> (example: <code>BONUS200 200</code>)",
        "admin_promo_ok": "✅ Promo code <b>{code}</b> for <b>{reward} ⭐</b> added.",
        "admin_stats": "📊 <b>Statistics</b>\nUsers in DB: <b>{users}</b>\nTotal balance in bot: <b>{stars} ⭐</b>",
        "back": "⬅️ Back",
    },
}


def t(user_id: int, key: str, **kwargs) -> str:
    lang = get_user_lang(user_id)
    template = TEXTS.get(lang, TEXTS["ru"]).get(key, TEXTS["ru"][key])
    return template.format(**kwargs) if kwargs else template


def write_json_file(
    users: dict[int, dict],
    cases: dict[str, dict],
    promos: dict[str, int] | None = None,
) -> None:
    payload = {
        "users": {
            str(k): {
                "balance": max(0, int(v.get("balance", 0))),
                "lang": v.get("lang") if v.get("lang") in ("ru", "en") else "ru",
                "used_promos": list(dict.fromkeys(str(p).upper() for p in v.get("used_promos", []))),
            }
            for k, v in users.items()
        },
        "cases": cases,
        "promos": promos if promos is not None else DEFAULT_PROMOS,
    }
    tmp_file = f"{DATA_FILE}.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp_file, DATA_FILE)


def load_data() -> tuple[dict[int, dict], dict[str, dict], dict[str, int]]:
    if not os.path.exists(DATA_FILE):
        cases_copy = {k: dict(v) for k, v in DEFAULT_CASES.items()}
        promos_copy = dict(DEFAULT_PROMOS)
        write_json_file({}, cases_copy, promos_copy)
        return {}, cases_copy, promos_copy

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError):
        cases_copy = {k: dict(v) for k, v in DEFAULT_CASES.items()}
        promos_copy = dict(DEFAULT_PROMOS)
        return {}, cases_copy, promos_copy

    raw_users = raw.get("users", {})
    users: dict[int, dict] = {}
    if isinstance(raw_users, dict):
        for uid_str, val in raw_users.items():
            if str(uid_str).isdigit():
                uid = int(uid_str)
                if isinstance(val, dict):
                    lang_val = val.get("lang")
                    users[uid] = {
                        "balance": max(0, int(val.get("balance", 0))),
                        "lang": lang_val if lang_val in ("ru", "en") else "ru",
                        "used_promos": list(dict.fromkeys(str(p).upper() for p in val.get("used_promos", []))),
                    }
                else:
                    users[uid] = {
                        "balance": max(0, int(val)),
                        "lang": "ru",
                        "used_promos": [],
                    }

    raw_cases = raw.get("cases", {})
    cases: dict[str, dict] = {}
    for cid, default_cfg in DEFAULT_CASES.items():
        saved_cfg = raw_cases.get(cid, {}) if isinstance(raw_cases, dict) else {}
        cases[cid] = {
            "name": str(saved_cfg.get("name", default_cfg["name"])),
            "price": max(1, int(saved_cfg.get("price", default_cfg["price"]))),
            "reward_min": int(saved_cfg.get("reward_min", default_cfg["reward_min"])),
            "reward_max": int(saved_cfg.get("reward_max", default_cfg["reward_max"])),
        }

    raw_promos = raw.get("promos", DEFAULT_PROMOS)
    promos: dict[str, int] = {}
    if isinstance(raw_promos, dict):
        for code, reward in raw_promos.items():
            clean_code = str(code).strip().upper()
            try:
                val_reward = int(reward)
            except (TypeError, ValueError):
                continue
            if clean_code and val_reward > 0:
                promos[clean_code] = val_reward
    if not promos:
        promos = dict(DEFAULT_PROMOS)

    return users, cases, promos


users_db, cases_db, promos_db = load_data()


def save_data() -> None:
    write_json_file(users_db, cases_db, promos_db)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

pending_inputs: dict[int, dict] = {}


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def ensure_user(user_id: int) -> dict:
    if user_id not in users_db:
        users_db[user_id] = {
            "balance": 0,
            "lang": "ru",
            "used_promos": [],
        }
        save_data()
    return users_db[user_id]


def get_user_lang(user_id: int) -> str:
    rec = ensure_user(user_id)
    lang = rec.get("lang")
    return lang if lang in ("ru", "en") else "ru"


def set_user_lang(user_id: int, lang: str) -> None:
    rec = ensure_user(user_id)
    rec["lang"] = "en" if lang == "en" else "ru"
    save_data()


def get_user_balance(user_id: int) -> int:
    rec = ensure_user(user_id)
    return max(0, int(rec.get("balance", 0)))


def set_user_balance(user_id: int, new_balance: int) -> None:
    rec = ensure_user(user_id)
    rec["balance"] = max(0, int(new_balance))
    save_data()


def build_webapp_url(user_id: int) -> str:
    bal = get_user_balance(user_id)
    lang = get_user_lang(user_id)
    prices_map = {cid: cfg["price"] for cid, cfg in cases_db.items()}
    encoded_prices = base64.urlsafe_b64encode(
        json.dumps(prices_map, ensure_ascii=False).encode("utf-8")
    ).decode("ascii")
    sep = "&" if "?" in URL_WEBAPP else "?"
    return f"{URL_WEBAPP}{sep}balance={bal}&lang={lang}&prices={encoded_prices}"


def lang_choice_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Русский (RU)", callback_data="set_lang:ru"),
                InlineKeyboardButton(text="English (EN)", callback_data="set_lang:en"),
            ]
        ]
    )


def main_menu_kb(user_id: int) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=t(user_id, "btn_open"), web_app=WebAppInfo(url=build_webapp_url(user_id)))],
        [
            KeyboardButton(text=t(user_id, "btn_topup")),
            KeyboardButton(text=t(user_id, "btn_promo")),
        ],
        [KeyboardButton(text=t(user_id, "btn_change_lang"))],
    ]
    if is_admin(user_id):
        rows.append([KeyboardButton(text=t(user_id, "btn_admin"))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def topup_amounts_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="10 ⭐", callback_data="topup_stars:10"),
                InlineKeyboardButton(text="50 ⭐", callback_data="topup_stars:50"),
                InlineKeyboardButton(text="100 ⭐", callback_data="topup_stars:100"),
            ],
            [InlineKeyboardButton(text=t(user_id, "btn_custom_amount"), callback_data="topup_custom")],
        ]
    )


def admin_panel_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(user_id, "admin_btn_balance"), callback_data="admin_set_balance")],
            [InlineKeyboardButton(text=t(user_id, "admin_btn_prices"), callback_data="admin_edit_prices")],
            [InlineKeyboardButton(text=t(user_id, "admin_btn_promo"), callback_data="admin_add_promo")],
            [InlineKeyboardButton(text=t(user_id, "admin_btn_stats"), callback_data="admin_stats")],
        ]
    )


def admin_cases_price_kb(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{c['name']} — {c['price']} ⭐",
                callback_data=f"admin_case_price:{cid}",
            )
        ]
        for cid, c in cases_db.items()
    ]
    buttons.append([InlineKeyboardButton(text=t(user_id, "back"), callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def send_stars_invoice(chat_id: int, user_id: int, stars_amount: int) -> None:
    await bot.send_invoice(
        chat_id=chat_id,
        title=t(user_id, "invoice_title"),
        description=t(user_id, "invoice_desc", stars=stars_amount),
        payload=json.dumps({"action": "topup", "stars": stars_amount}),
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=t(user_id, "invoice_label", stars=stars_amount), amount=stars_amount)],
    )


async def send_language_selected_menu(chat_id: int, user_id: int) -> None:
    bal = get_user_balance(user_id)
    lang_name = t(user_id, "lang_name")
    await bot.send_message(
        chat_id=chat_id,
        text=t(user_id, "lang_selected", lang_name=lang_name, bal=bal),
        reply_markup=main_menu_kb(user_id),
    )


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    uid = message.from_user.id
    ensure_user(uid)
    pending_inputs.pop(uid, None)
    await message.answer(
        t(uid, "choose_lang"),
        reply_markup=lang_choice_kb(),
    )


@dp.callback_query(F.data.startswith("set_lang:"))
async def cb_set_lang(callback: CallbackQuery) -> None:
    await callback.answer()
    uid = callback.from_user.id
    chosen = callback.data.split(":", 1)[1]
    set_user_lang(uid, chosen)
    await send_language_selected_menu(callback.message.chat.id, uid)


@dp.message(F.text.in_({"Сменить язык", "Change language"}))
async def btn_change_lang(message: Message) -> None:
    uid = message.from_user.id
    await message.answer(
        t(uid, "choose_lang"),
        reply_markup=lang_choice_kb(),
    )


@dp.message(F.text.in_({"Промокод", "Promo code"}))
async def btn_promo(message: Message) -> None:
    uid = message.from_user.id
    pending_inputs[uid] = {"mode": "enter_promo"}
    await message.answer(t(uid, "ask_promo"))


@dp.message(F.text.in_({"Пополнить", "Top up"}))
async def btn_topup(message: Message) -> None:
    uid = message.from_user.id
    await message.answer(
        t(uid, "ask_topup_amount"),
        reply_markup=topup_amounts_kb(uid),
    )


@dp.callback_query(F.data.startswith("topup_stars:"))
async def cb_topup_preset(callback: CallbackQuery) -> None:
    await callback.answer()
    uid = callback.from_user.id
    amount = int(callback.data.split(":", 1)[1])
    await send_stars_invoice(callback.message.chat.id, uid, amount)


@dp.callback_query(F.data == "topup_custom")
async def cb_topup_custom(callback: CallbackQuery) -> None:
    await callback.answer()
    uid = callback.from_user.id
    pending_inputs[uid] = {"mode": "custom_topup"}
    await callback.message.answer(t(uid, "ask_custom_amount"))


@dp.message(Command("admin"))
@dp.message(F.text.in_({"🛠 Админ-панель", "🛠 Admin panel"}))
async def open_admin_panel(message: Message) -> None:
    uid = message.from_user.id
    if not is_admin(uid):
        await message.answer(t(uid, "no_admin"))
        return
    await message.answer(
        t(uid, "admin_title"),
        parse_mode="HTML",
        reply_markup=admin_panel_kb(uid),
    )


@dp.callback_query(F.data == "admin_back")
async def cb_admin_back(callback: CallbackQuery) -> None:
    uid = callback.from_user.id
    if not is_admin(uid):
        return
    await callback.answer()
    await callback.message.edit_text(
        t(uid, "admin_title"),
        parse_mode="HTML",
        reply_markup=admin_panel_kb(uid),
    )


@dp.callback_query(F.data == "admin_set_balance")
async def cb_admin_set_balance(callback: CallbackQuery) -> None:
    uid = callback.from_user.id
    if not is_admin(uid):
        return
    await callback.answer()
    pending_inputs[uid] = {"mode": "admin_set_balance"}
    await callback.message.answer(t(uid, "admin_ask_balance"), parse_mode="HTML")


@dp.callback_query(F.data == "admin_edit_prices")
async def cb_admin_edit_prices(callback: CallbackQuery) -> None:
    uid = callback.from_user.id
    if not is_admin(uid):
        return
    await callback.answer()
    await callback.message.edit_text(
        t(uid, "admin_ask_case"),
        reply_markup=admin_cases_price_kb(uid),
    )


@dp.callback_query(F.data.startswith("admin_case_price:"))
async def cb_admin_choose_case_price(callback: CallbackQuery) -> None:
    uid = callback.from_user.id
    if not is_admin(uid):
        return
    await callback.answer()
    case_id = callback.data.split(":", 1)[1]
    if case_id not in cases_db:
        return
    pending_inputs[uid] = {"mode": "admin_case_price", "case_id": case_id}
    await callback.message.answer(
        t(uid, "admin_ask_price", name=cases_db[case_id]["name"]),
        parse_mode="HTML",
    )


@dp.callback_query(F.data == "admin_add_promo")
async def cb_admin_add_promo(callback: CallbackQuery) -> None:
    uid = callback.from_user.id
    if not is_admin(uid):
        return
    await callback.answer()
    pending_inputs[uid] = {"mode": "admin_add_promo"}
    await callback.message.answer(t(uid, "admin_ask_promo"), parse_mode="HTML")


@dp.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery) -> None:
    uid = callback.from_user.id
    if not is_admin(uid):
        return
    await callback.answer()
    total_users = len(users_db)
    total_stars = sum(max(0, int(u.get("balance", 0))) for u in users_db.values())
    await callback.message.answer(
        t(uid, "admin_stats", users=total_users, stars=total_stars),
        parse_mode="HTML",
    )


@dp.message(F.web_app_data)
async def handle_webapp_data(message: Message) -> None:
    uid = message.from_user.id
    try:
        data = json.loads(message.web_app_data.data)
    except (json.JSONDecodeError, TypeError):
        return
    if not isinstance(data, dict):
        return
    action = data.get("action")

    if action == "open_topup":
        try:
            needed = max(0, int(data.get("needed", 0) or 0))
        except (TypeError, ValueError):
            needed = 0
        text = t(uid, "webapp_topup_needed", needed=needed) if needed > 0 else t(uid, "webapp_topup_default")
        await message.answer(text, parse_mode="HTML", reply_markup=topup_amounts_kb(uid))
        return

    if action == "open_case":
        case_id = data.get("case_id")
        case_info = cases_db.get(case_id)
        if not case_info:
            await message.answer(t(uid, "case_not_found"), reply_markup=main_menu_kb(uid))
            return

        price = int(case_info["price"])
        bal = get_user_balance(uid)
        if bal < price:
            missing = price - bal
            await message.answer(
                t(uid, "not_enough_stars", missing=missing),
                parse_mode="HTML",
                reply_markup=main_menu_kb(uid),
            )
            return

        r_min = int(case_info["reward_min"])
        r_max = int(case_info["reward_max"])
        if r_min > r_max:
            r_min, r_max = r_max, r_min
        drop = random.randint(r_min, r_max)
        new_bal = bal - price + drop
        set_user_balance(uid, new_bal)

        await message.answer(
            t(uid, "case_opened", name=case_info["name"], price=price, drop=drop, bal=new_bal),
            parse_mode="HTML",
            reply_markup=main_menu_kb(uid),
        )
        return

    if action == "upgrade":
        try:
            source_val = int(data.get("source", 0))
            target_val = int(data.get("target", 0))
        except (TypeError, ValueError):
            return
        if source_val <= 0 or target_val <= 0:
            return
        bal = get_user_balance(uid)

        if bal < source_val:
            await message.answer(
                t(uid, "not_enough_stars", missing=source_val - bal),
                parse_mode="HTML",
                reply_markup=main_menu_kb(uid),
            )
            return

        win_chance = min(0.9, (source_val / target_val) * 0.9)
        if random.random() <= win_chance:
            new_bal = bal - source_val + target_val
            set_user_balance(uid, new_bal)
            await message.answer(
                t(uid, "upgrade_success", target=target_val, bal=new_bal),
                parse_mode="HTML",
                reply_markup=main_menu_kb(uid),
            )
        else:
            new_bal = bal - source_val
            set_user_balance(uid, new_bal)
            await message.answer(
                t(uid, "upgrade_fail", source=source_val, bal=new_bal),
                parse_mode="HTML",
                reply_markup=main_menu_kb(uid),
            )


@dp.message(F.text)
async def handle_pending_text(message: Message) -> None:
    uid = message.from_user.id
    state = pending_inputs.get(uid)
    if not state:
        return

    mode = state["mode"]
    raw = (message.text or "").strip()

    if mode == "enter_promo":
        pending_inputs.pop(uid, None)
        code = raw.upper()
        reward = promos_db.get(code)
        if not reward:
            await message.answer(t(uid, "promo_not_found"), reply_markup=main_menu_kb(uid))
            return
        rec = ensure_user(uid)
        used = rec.setdefault("used_promos", [])
        if code in used:
            await message.answer(t(uid, "promo_already_used"), reply_markup=main_menu_kb(uid))
            return
        used.append(code)
        new_bal = get_user_balance(uid) + int(reward)
        set_user_balance(uid, new_bal)
        await message.answer(
            t(uid, "promo_activated", code=code, reward=reward, bal=new_bal),
            parse_mode="HTML",
            reply_markup=main_menu_kb(uid),
        )
        return

    if mode == "custom_topup":
        if not raw.isdigit() or int(raw) < 1:
            await message.answer(t(uid, "invalid_positive_int"))
            return
        pending_inputs.pop(uid, None)
        await send_stars_invoice(message.chat.id, uid, int(raw))
        return

    if mode == "admin_set_balance" and is_admin(uid):
        parts = raw.split()
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
            await message.answer(t(uid, "admin_bad_balance"), parse_mode="HTML")
            return
        target_uid = int(parts[0])
        new_bal = int(parts[1])
        ensure_user(target_uid)
        set_user_balance(target_uid, new_bal)
        pending_inputs.pop(uid, None)
        await message.answer(
            t(uid, "admin_balance_ok", uid=target_uid, bal=new_bal),
            parse_mode="HTML",
        )
        return

    if mode == "admin_case_price" and is_admin(uid):
        if not raw.isdigit() or int(raw) < 1:
            await message.answer(t(uid, "invalid_positive_int"))
            return
        case_id = state["case_id"]
        if case_id not in cases_db:
            pending_inputs.pop(uid, None)
            return
        new_price = int(raw)
        cases_db[case_id]["price"] = new_price
        save_data()
        pending_inputs.pop(uid, None)
        await message.answer(
            t(uid, "admin_price_ok", name=cases_db[case_id]["name"], price=new_price),
            parse_mode="HTML",
        )
        return

    if mode == "admin_add_promo" and is_admin(uid):
        parts = raw.split()
        if len(parts) != 2 or not parts[1].isdigit() or int(parts[1]) < 1:
            await message.answer(t(uid, "admin_bad_promo"), parse_mode="HTML")
            return
        code = parts[0].strip().upper()
        if not code:
            await message.answer(t(uid, "admin_bad_promo"), parse_mode="HTML")
            return
        reward = int(parts[1])
        promos_db[code] = reward
        save_data()
        pending_inputs.pop(uid, None)
        await message.answer(
            t(uid, "admin_promo_ok", code=code, reward=reward),
            parse_mode="HTML",
        )


@dp.pre_checkout_query()
async def on_pre_checkout(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(ok=True)


@dp.message(F.successful_payment)
async def on_successful_payment(message: Message) -> None:
    uid = message.from_user.id
    paid_stars = int(message.successful_payment.total_amount)
    new_bal = get_user_balance(uid) + paid_stars
    set_user_balance(uid, new_bal)
    await message.answer(
        t(uid, "payment_ok", stars=paid_stars, bal=new_bal),
        parse_mode="HTML",
        reply_markup=main_menu_kb(uid),
    )


async def main() -> None:
    save_data()
    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
