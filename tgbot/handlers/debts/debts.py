from aiogram.types import Message

from pathlib import Path
from tgbot.filters.user_type import UserTypeFilter
from tgbot.models.database_instance import db
import tgbot.keyboards.reply as rkb
import gspread

from tgbot.misc.decorators.log_decorator import log_function_call


with open(F"{Path(__file__).parent.parent.parent.parent.absolute()}/teachers.txt", encoding='utf-8') as f:
    teachers_list = [key.strip() for key in f]

#Список преподов
teachers_text = ""
teacher, comment = '', ''
for index, pers in enumerate(teachers_list):
    teachers_text += "\n" if index % 3 == 0 else " | "
    teachers_text += f"<code> {pers} </code>"

#Запись в таблицу
def save_data_to_gheet(teacher: str, person: str, comment: str) -> int:
#Проверяет клетку на наличие информации
    def update_cell(row, col):
        if str(sh.cell(row, col)) == f'<Cell R{row}C{col} None>':
            sh.update_cell(row, col, f"{person}\n{comment}")
            return 0
        update_cell(row+1, col)
        
    gc = gspread.service_account("creds.json")
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1H-_KBljgZ8kWe8rgmPZOJ47JurGm7b3wbnODpP1g3Jg/edit#gid=0").sheet1

#Поиск препода в таблице
    for x in sh.get_all_cells():
        if teacher in str(x):
            row, col = x.row, x.col
            return update_cell(row, col)


@log_function_call
async def get_teachers(message: Message):
    if message.text == "Отмена":
        await message.delete()
        await message.answer(text="Меню студента", reply_markup=rkb.student_keyboard)
    else:   
        await message.answer(text="Выберете преподавателя")
        await message.answer(text=teachers_text, parse_mode="HTML")

@log_function_call
async def get_text_message(message: Message) -> str:
    global teacher
    teacher = message.text.strip()
    if teacher not in teachers_list:
        await message.reply("Неправильно введн преподаватель, попробуйте еще раз.")
        return await get_teachers(message)
    
    await message.reply("Оставьте преподавателю комментарий")

@log_function_call
async def save_resuts(message: Message):
    global comment, teacher

    if teacher not in teachers_list:
        return await get_text_message(message)

    comment = message.text.strip()
    await message.reply(text="Записываю данные в таблицу...", reply_markup=rkb.student_keyboard)
    
    save_data_to_gheet(teacher, await db.get_fio(message.from_user.id), comment)
    comment, teacher = '', ''
        
def register_debts_check(dp):
    dp.register_message_handler(get_teachers, UserTypeFilter("student"), content_types=['text'], text=['Записаться', "Отмена"])
    dp.register_message_handler(get_text_message, UserTypeFilter("student"), content_types=['text'], text=teachers_list)
    dp.register_message_handler(save_resuts, UserTypeFilter("student"), content_types=['text'])