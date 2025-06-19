from aiogram import Router, F, types
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from keyboards import main_menu, wallet_keyboard, withdraw_options, p2p_menu, exchange_menu, back_button
from keyboards.inline import CRYPTO_ADDRESSES
from aiogram.fsm.state import State, StatesGroup
import sqlite3
import datetime
from config_reader import config

admin = int(config.admin_id.get_secret_value())

router = Router()

def get_balance(user_id):
    with sqlite3.connect('exchange.sqlite3') as conn:
        return conn.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]

def get_user_id_by_username(username):
    with sqlite3.connect('exchange.sqlite3') as conn:
        result = conn.execute('SELECT user_id FROM users WHERE username = ?', (username,)).fetchone()
        return result[0] if result else None

def save_support_message(user_id, message_text):
    with sqlite3.connect('exchange.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO support_messages (user_id, message, timestamp) VALUES (?, ?, ?)",
            (user_id, message_text, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()
        return cursor.lastrowid

def save_admin_response(message_id, admin_id, response_text):
    with sqlite3.connect('exchange.sqlite3') as conn:
        conn.execute(
            "UPDATE support_messages SET admin_id = ?, response = ? WHERE id = ?",
            (admin_id, response_text, message_id)
        )
        conn.commit()

class SupportState(StatesGroup):
    wait_for_msg = State()
    wait_for_admin_reply = State()

class SetBalanceState(StatesGroup):
    uname = State()
    balance = State()

class P2PState(StatesGroup):
    wait_for_amount = State()
    wait_for_price = State()

class ExchangeState(StatesGroup):
    wait_for_amount = State()
    from_currency = State()
    to_currency = State()

def get_balances(user_id):
    with sqlite3.connect('exchange.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT currency, amount 
            FROM balances 
            WHERE user_id = ?
        ''', (user_id,))
        return dict(cursor.fetchall())

def update_balance(user_id, currency, amount):
    with sqlite3.connect('exchange.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO balances (user_id, currency, amount)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, currency) 
            DO UPDATE SET amount = amount + ?
        ''', (user_id, currency, amount, amount))
        conn.commit()

@router.message(CommandStart())
async def send_welcome(msg: Message):
    user_id = msg.from_user.id
    username = msg.from_user.username
    full_name = msg.from_user.full_name

    with sqlite3.connect('exchange.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        conn.commit()

    await msg.answer(
        "Добро пожаловать в криптовалютный обменник!\n\n"
        "Выберите нужный раздел в меню ниже:",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "back")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "topup")
async def topup_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите валюту для пополнения:",
        reply_markup=wallet_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("currency_"))
async def currency_handler(callback: types.CallbackQuery):
    currency = callback.data.replace("currency_", "")
    address = CRYPTO_ADDRESSES[currency]
    
    await callback.message.edit_text(
        f"Для пополнения {currency} используйте следующий адрес:\n\n"
        f"`{address}`\n\n"
        "После отправки средств, они будут автоматически зачислены на ваш баланс.",
        reply_markup=back_button(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "withdraw")
async def withdraw_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите способ вывода средств:",
        reply_markup=withdraw_options()
    )
    await callback.answer()

@router.callback_query(F.data.in_(["withdraw_usdt", "withdraw_uah"]))
async def withdraw_option_handler(callback: types.CallbackQuery):
    option = callback.data.replace("withdraw_", "")
    currency = "USDT" if option == "usdt" else "UAH"
    
    await callback.message.edit_text(
        f"Для вывода {currency} свяжитесь с администратором через кнопку ниже.\n\n"
        "Укажите:\n"
        "1. Сумму вывода\n"
        "2. Реквизиты для получения средств",
        reply_markup=back_button()
    )
    await callback.answer()

@router.callback_query(F.data == "p2p")
async def p2p_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "P2P обмен:\n\n"
        "Здесь вы можете купить или продать криптовалюту "
        "с переводом на карту или электронный кошелек.",
        reply_markup=p2p_menu()
    )
    await callback.answer()

@router.callback_query(F.data.in_(["p2p_buy", "p2p_sell"]))
async def p2p_trade_handler(callback: types.CallbackQuery, state: FSMContext):
    trade_type = "покупки" if callback.data == "p2p_buy" else "продажи"
    await state.set_state(P2PState.wait_for_amount)
    await state.update_data(trade_type=trade_type)
    
    await callback.message.edit_text(
        f"Выберите валюту для {trade_type}:",
        reply_markup=wallet_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "exchange")
async def exchange_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Обмен криптовалют:\n\n"
        "В этом разделе вы можете обменять одну криптовалюту на другую.",
        reply_markup=exchange_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "wallet")
async def wallet_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balances = get_balances(user_id)
    
    if not balances:
        text = "У вас пока нет средств на балансе."
    else:
        text = "Ваш баланс:\n\n"
        for currency, amount in balances.items():
            text += f"{currency}: {amount}\n"
    
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "support")
async def support_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Связь с администратором:\n\n"
        "Опишите вашу проблему или вопрос. "
        "Мы ответим вам в ближайшее время.",
        reply_markup=back_button()
    )
    await state.set_state(SupportState.wait_for_msg)
    await callback.answer()

@router.message(SupportState.wait_for_msg)
async def process_support_message(msg: Message, state: FSMContext):
    user = msg.from_user
    message_id = save_support_message(user.id, msg.text)
    
    admin_message = (
        f"Новое обращение #{message_id}\n"
        f"Пользователь: {user.full_name} (@{user.username})\n"
        f"ID: {user.id}\n"
        f"Сообщение:\n{msg.text}"
    )
    
    try:
        await msg.bot.send_message(
            admin,
            admin_message,
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[
                types.InlineKeyboardButton(
                    text="Ответить",
                    callback_data=f"reply_{message_id}"
                )
            ]])
        )
        await msg.answer("Ваше сообщение отправлено администратору. Ожидайте ответа.", reply_markup=back_button())
    except Exception as e:
        await msg.answer("Не удалось отправить сообщение администратору.", reply_markup=back_button())
        print(f"Error sending to admin: {e}")
    
    await state.clear()

@router.callback_query(F.data.startswith("reply_"))
async def admin_reply_handler(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != admin:
        await callback.answer("У вас нет прав для этой команды", show_alert=True)
        return
    
    message_id = int(callback.data.replace("reply_", ""))
    await state.set_state(SupportState.wait_for_admin_reply)
    await state.update_data(message_id=message_id)
    
    await callback.message.edit_text(
        "Введите ваш ответ пользователю:"
    )
    await callback.answer()

@router.message(SupportState.wait_for_admin_reply)
async def process_admin_reply(msg: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data['message_id']
    
    with sqlite3.connect('exchange.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id FROM support_messages WHERE id = ?",
            (message_id,)
        )
        user_id = cursor.fetchone()[0]
        
        cursor.execute(
            "UPDATE support_messages SET admin_id = ?, response = ? WHERE id = ?",
            (msg.from_user.id, msg.text, message_id)
        )
        conn.commit()
    
    try:
        await msg.bot.send_message(
            user_id,
            f"Ответ администратора на ваше обращение #{message_id}:\n\n{msg.text}",
            reply_markup=back_button()
        )
        await msg.answer("Ответ отправлен пользователю", reply_markup=back_button())
    except Exception as e:
        await msg.answer("Не удалось отправить ответ пользователю", reply_markup=back_button())
        print(f"Error sending reply: {e}")
    
    await state.clear()

@router.message(Command('set_balance'))
async def set_balance_handler(msg: Message, state: FSMContext):
    if msg.from_user.id == admin:
        await msg.answer("Введите username пользователя:")
        await state.set_state(SetBalanceState.uname)
    else:
        await msg.answer("У вас нет прав для этой команды")
