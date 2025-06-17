from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import types
import sqlite3

CRYPTO_ADDRESSES = {
    "BTC": "bc1qfcgcf6d8l38pf25ws0tfyhkj46msjxetrd4q3d",
    "ETH": "0x7B71507a8c8Ee73680E5D3Aec9cf5EAc8eB2b8A6",
    "USDT ETH20": "0x7B71507a8c8Ee73680E5D3Aec9cf5EAc8eB2b8A6",
    "BNB": "0x7B71507a8c8Ee73680E5D3Aec9cf5EAc8eB2b8A6",
    "USDC ETH20": "0x7B71507a8c8Ee73680E5D3Aec9cf5EAc8eB2b8A6",
    "SOLANA": "Eh5J6XrhUUGMKsv7awGeaRJ5HSs2XK3SLqQegRMurdd9",
    "LTC": "ltc1q8sjz2srll828p46a34esf7gvcujwm2gt6f72kr",
    "TRX": "TUHm6RTY9dhheStPCifDp3PR5AMBsmvjFG",
    "BTC CASH": "qrh6ql4anlc0m70khrzwxnrrf65ynagh7c003jqczk",
    "USDT TRC20": "0x7B71507a8c8Ee73680E5D3Aec9cf5EAc8eB2b8A6"
}


#главное меню
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text='Пополнить', callback_data='topup'),
        types.InlineKeyboardButton(text='Вывести', callback_data='withdraw')
    )
    builder.row(
        types.InlineKeyboardButton(text='P2P', callback_data='p2p'),
        types.InlineKeyboardButton(text='Обмен', callback_data='exchange')
    )
    builder.row(
        types.InlineKeyboardButton(text='Кошелек', callback_data='wallet'),
        types.InlineKeyboardButton(text='Администратор', callback_data='support')
    )
    
    return builder.as_markup()

#валюты
def wallet_keyboard():
    builder = InlineKeyboardBuilder()
    for currency in CRYPTO_ADDRESSES:
        builder.add(types.InlineKeyboardButton(
            text=currency,
            callback_data=f"currency_{currency}"
        ))
    builder.add(InlineKeyboardButton(text='Главное меню', callback_data='back'))
    builder.adjust(2)
    return builder.as_markup()

#вывод средств
def withdraw_options():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text='USDT', callback_data='withdraw_usdt'),
        types.InlineKeyboardButton(text='Гривны', callback_data='withdraw_uah')
    )
    builder.row(
        types.InlineKeyboardButton(text='Главное меню', callback_data='back')
    )
    return builder.as_markup()

def p2p_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text='Купить', callback_data='p2p_buy'),
        types.InlineKeyboardButton(text='Продать', callback_data='p2p_sell')
    )
    builder.row(
        types.InlineKeyboardButton(text='Мои ордера', callback_data='p2p_my_orders'),
        types.InlineKeyboardButton(text='Активные ордера', callback_data='p2p_active_orders')
    )
    builder.row(
        types.InlineKeyboardButton(text='Главное меню', callback_data='back')
    )
    return builder.as_markup()

def exchange_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text='Выбрать валюту для обмена', callback_data='exchange_from'),
        types.InlineKeyboardButton(text='Выбрать валюту для получения', callback_data='exchange_to')
    )
    builder.row(
        types.InlineKeyboardButton(text='Главное меню', callback_data='back')
    )
    return builder.as_markup()

def back_button():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Главное меню', callback_data='back'))
    return builder.as_markup()

