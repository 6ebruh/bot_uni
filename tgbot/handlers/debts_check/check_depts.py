from aiogram.types import Message

from pathlib import Path
from tgbot.filters.user_type import UserTypeFilter
from tgbot.models.database_instance import db
import tgbot.keyboards.reply as rkb
import gspread

from tgbot.misc.decorators.log_decorator import log_function_call


with open(F"{Path(__file__).parent.parent.parent.parent.absolute()}/teachers.txt", encoding='utf-8') as f:
    teachers_list = [key.strip() for key in f]

def check_table(teacher: str) -> int:
    gc = gspread.service_account("creds.json")
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1H-_KBljgZ8kWe8rgmPZOJ47JurGm7b3wbnODpP1g3Jg/edit#gid=0").sheet1
    message = ""
    for x in sh.get_all_cells():
        if teacher in str(x.value):
            index, row, col = 0, x.row, x.col
            while True:
                index, row = index + 1, row + 1
                if sh.cell(row, col).value == None:
                    return message
                message += f'{index}. {str(sh.cell(row, col).value)}\n'

@log_function_call
async def whoami(message: Message):
        await message.delete()
        await message.answer(text="Получаю значения из таблицы...")
        
        await message.answer(text=check_table(str((await db.get_user_ln(message.from_user.id))[0])), reply_markup=rkb.teacher_keyboard)

#хендлер
def register_debts_check_teacher(dp):
    dp.register_message_handler(whoami, UserTypeFilter("teacher"), content_types=['text'], text="Получить пересдачи")
