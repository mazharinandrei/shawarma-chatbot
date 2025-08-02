from telebot import types
from db import BotDB


db = BotDB('db.db')

remove_keyboard = types.ReplyKeyboardRemove()

main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_markup.add(types.KeyboardButton("📄 Меню"),
                types.KeyboardButton("🍱 Корзина"))

cart_markup = types.InlineKeyboardMarkup(row_width=2)
cart_markup.add(types.InlineKeyboardButton("✔ Оформить заказ", callback_data="place_order"))
cart_markup.add(types.InlineKeyboardButton("🗣 Связаться с оператором", callback_data="operator"))
cart_markup.add(types.InlineKeyboardButton("📝 Изменить заказ", callback_data="change_order"))

pay_markup = types.InlineKeyboardMarkup(row_width=2)
pay_markup.add(types.InlineKeyboardButton("💸 Наличными", callback_data="cash"))
pay_markup.add(types.InlineKeyboardButton("💳 Картой курьеру", callback_data="card"))


def get_delivered_markup(user_id):
    delivered_markup = types.InlineKeyboardMarkup(row_width=2)
    delivered_markup.add(types.InlineKeyboardButton("Заказ доставлен", callback_data=f"end_order_{user_id}"))
    return delivered_markup

def delete_markup(cart):
    delete_markup = types.InlineKeyboardMarkup(row_width=2)
    for i in range(len(cart)):
        delete_markup.add(types.InlineKeyboardButton(f"{cart[i][0]} {cart[i][1]}{cart[i][2]} - {cart[i][3]}₽", callback_data="delete_"+str(i)))
    delete_markup.add(types.InlineKeyboardButton("✔ Оформить заказ", callback_data="place_order"))
    delete_markup.add(types.InlineKeyboardButton("🗣 Связаться с оператором", callback_data="operator"))
    return delete_markup

def get_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)  # Меню
    categories = db.get_categories()
    for category in categories:
        markup.add(types.InlineKeyboardButton(category[0], callback_data=category[1]))
    markup.add(types.InlineKeyboardButton("⁉️ Я не знаю, что заказать", callback_data="help"))
    return markup


def get_subcategory_markup(callback):
    markup = types.InlineKeyboardMarkup(row_width=1)
    categories = db.get_tastes(callback)
    for category in categories:
        markup.add(types.InlineKeyboardButton(category[0], callback_data=category[1]))
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu"))
    return markup


def get_food_markup(callback):
    food = db.get_food_info(callback)
    markup = types.InlineKeyboardMarkup(row_width=len(food))
    for item in food:
        markup.add(types.InlineKeyboardButton(f"{item[2]} {item[3]} - {item[1]}₽", callback_data=str(item[4])+"/"+ str(item[2])))
    food_category = db.get_category_of_food(callback)
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_" + str(food_category)))
    return markup

def get_random_food_markup(callback):
    food = db.get_food_info(callback)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("◀️  Назад", callback_data="previous_food"),
               types.InlineKeyboardButton("▶️  Дальше", callback_data="next_food"))
    for item in food:
        markup.add(types.InlineKeyboardButton(f"{item[2]} {item[3]} - {item[1]}₽", callback_data=str(item[4])+"/"+ str(item[2])))
    return markup


phone_button = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
phone_button.add(types.KeyboardButton(text="Отправить телефон", request_contact=True))


address_check_markup = types.InlineKeyboardMarkup()
address_check_markup.add(types.InlineKeyboardButton("Всё верно", callback_data="yes"),
                         types.InlineKeyboardButton("Изменить адрес", callback_data="no"))
