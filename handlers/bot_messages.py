from aiogram import Router, F
from aiogram.types import Message
from keyboards import back_button

router = Router()

@router.message()
async def handle_unknown_message(msg: Message):
    await msg.answer(
        "Пожалуйста, используйте кнопки меню для навигации.",
        reply_markup=back_button()
    )
