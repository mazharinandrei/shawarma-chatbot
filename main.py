import telebot  # библиотека бота
import config  # в конфиге хранятся секретнейшие данные бота
import keyboards  # отдельный файл для всех кнопок бота
from db import BotDB
from random import shuffle

bot = telebot.TeleBot(config.token)  # инициализация бота
db = BotDB('db.db')

i = 0


@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Для начала отправьте свой номер телефона",
                     reply_markup=keyboards.phone_button)  # Приветствуем нашего клиента, просим поделиться номером
    # телефона с помощью кнопки
    bot.register_next_step_handler(message, contact)  # Получение следующего сообщения и переход к функции contact


def contact(message):
    if message.contact is not None:  # Если пользователь отправил контакт, а не что-то другое
        if db.check_phone_number(message.contact.phone_number) is not None:
            bot.send_message(message.chat.id, f"С возвращением, {message.chat.first_name}!\n"
                                              f"Ваш адрес: {db.get_user_address(message.from_user.id)}\n")

            bot.send_message(message.chat.id, f"Всё верно?", reply_markup=keyboards.address_check_markup)
        else:
            db.add_new_user(user_id=message.from_user.id,
                            first_name=message.from_user.first_name,
                            last_name=message.from_user.last_name,
                            phone_number=message.contact.phone_number)

            bot.send_message(message.chat.id, "Отлично! Теперь отправьте адрес доставки",
                             reply_markup=keyboards.remove_keyboard)
            bot.register_next_step_handler(message, input_address)

    else:
        bot.send_message(message.chat.id, "Чтобы отправить номер телефона, "
                                          "нажмите на кнопку \"Отправить телефон\" ")
        bot.register_next_step_handler(message, contact)  # перезапуск функции


def input_address(message):
    db.set_address(message.from_user.id, message.text)
    bot.send_message(message.chat.id, "Ваш адрес: " + message.text, reply_markup=keyboards.remove_keyboard)
    bot.send_message(message.chat.id, "Всё верно?", reply_markup=keyboards.address_check_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'yes')
def address_check(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.from_user.id, "Отлично! Нажмите на кнопку меню для перехода к заказу.",
                     reply_markup=keyboards.main_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'no')
def address_check(call):
    bot.send_message(call.from_user.id, "Отправьте адрес доставки.")
    bot.register_next_step_handler(call.message, input_address)


@bot.message_handler(content_types=['text'])
def navigation(message):
    if message.text == "📄 Меню":
        menu_markup = keyboards.get_menu_markup()
        bot.send_message(message.chat.id, "Выберите категорию: ", reply_markup=menu_markup)
    elif message.text == "🍱 Корзина":
        cart = db.get_user_cart(message.chat.id)
        msg = "На данный момент в корзине:"
        cost = 0
        for item in cart:
            msg += f"\n{item[0]} {item[1]} {item[2]} - {item[3]}₽"
            cost += float(item[3])
        bot.send_message(message.chat.id,
                         msg + "\nИтого: " + str(cost) + "₽",
                         reply_markup=keyboards.cart_markup)  # Должна браться корзина пользователя из БД


@bot.callback_query_handler(func=lambda call: call.data == "help")
def help(call):
    global all_food
    all_food = db.get_all_food()
    shuffle(all_food)
    food = all_food[0]
    food_info = db.get_food_info(callback=food[3])[0]
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id - 1)
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    with open('Фотографии/' + str(food_info[6]), "rb") as photo:
        bot.send_photo(chat_id=call.from_user.id, photo=photo, caption=f"{food_info[0]}\n\n{food_info[5]}",
                       reply_markup=keyboards.get_random_food_markup(food[3]))


@bot.callback_query_handler(func=lambda call: call.data in ["previous_food", "next_food"])
def back(call):
    global i
    if call.data == "previous_food":
        i -= 1
    if call.data == "next_food":
        i += 1
    try:
        food = all_food[i]
    except:
        food = all_food[0]
    food_info = db.get_food_info(callback=food[3])[0]
    with open('Фотографии/' + str(food_info[6]), "rb") as photo:
        bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        bot.send_photo(chat_id=call.from_user.id, photo=photo, caption=f"{food_info[0]}\n\n{food_info[5]}",
                       reply_markup=keyboards.get_random_food_markup(food[3]))


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_menu')
def back(call):
    markup = keyboards.get_menu_markup()
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text="Выберите категорию: ", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'back_to_' in call.data)
def back(call):
    category = call.data[8:]
    markup = keyboards.get_subcategory_markup(category)
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    bot.send_message(chat_id=call.from_user.id, text="Выберите категорию: ", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in db.get_category_callbacks())
def send_subcategory(call):
    markup = keyboards.get_subcategory_markup(call.data)
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text="Выберите категорию: ", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in db.get_food_callbacks())
def send_food(call):
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    markup = keyboards.get_food_markup(call.data)
    food_info = db.get_food_info(call.data)[0]
    with open('Фотографии/' + str(food_info[6]), "rb") as photo:
        bot.send_photo(chat_id=call.from_user.id, photo=photo, caption=f"{food_info[0]}\n\n{food_info[5]}",
                       reply_markup=markup)


comment = ""


@bot.callback_query_handler(func=lambda call: "/" in call.data)
def bjhg(call):
    order_info = call.data.split('/')
    name = order_info[0]
    food_info = db.get_food_info(name)[0]
    count = order_info[1]
    item = (food_info[0], food_info[2], food_info[3], food_info[1])
    db.add_to_cart(user_id=call.from_user.id, name=name, count=count)
    bot.send_message(call.from_user.id, f"Добавлено в корзину:\n{item[0]} {item[1]} {item[2]} - {item[3]}₽\n")


@bot.callback_query_handler(func=lambda call: call.data == 'place_order')
def back(call):
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    bot.send_message(call.from_user.id, "Отлично, выберите способ оплаты: ",
                     reply_markup=keyboards.pay_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'operator')
def back(call):
    bot.send_message(call.from_user.id, "Напишите, что нужно передать оператору: ")
    bot.register_next_step_handler(call.message, operator)


def operator(message):
    global comment
    comment += message.text
    cart = db.get_user_cart(message.chat.id)
    bot.send_message(message.chat.id, "Отлично! Мы передадим это сообщение оператору!",
                     reply_markup=keyboards.delete_markup(cart))


@bot.callback_query_handler(func=lambda call: "delete_" in call.data)
def back(call):
    cart = db.get_user_cart(call.from_user.id)
    item = int(call.data.split("_")[1])  # Какой по счёту элемент в корзине
    db.delete_from_cart(user_id=call.from_user.id, callback_data=cart[item][4], weight=cart[item][1])  # float
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    cart.pop(item)  # Удаляем из массива cart значение по индексу, чтобы лишний раз не лезть в корзину
    bot.send_message(call.from_user.id, "Выберите, что нужно удалить:",
                     reply_markup=keyboards.delete_markup(cart))


@bot.callback_query_handler(func=lambda call: call.data == 'change_order')
def back(call):
    cart = db.get_user_cart(call.from_user.id)
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    bot.send_message(call.from_user.id, "Выберите, что нужно удалить:", reply_markup=keyboards.delete_markup(cart))


@bot.callback_query_handler(func=lambda call: 'end_order_' in call.data)
def end_order(call):
    user_id = call.data.split('_')[2]
    db.clear_cart(user_id)
    message = call.message.text.replace('Новый', 'Завершенный')
    bot.edit_message_text(chat_id=config.admin, message_id=call.message.message_id,
                          text=message)
    bot.send_message(user_id, "Ваш заказ успешно доставлен! Приятного аппетита!")


@bot.callback_query_handler(func=lambda call: call.data in ["cash", "card"])
def end_of_order(call):
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    bot.send_message(call.from_user.id, "Отлично! Заказ придёт в течении 40 минут!")
    msg = "Новый заказ №1:\n"
    cart = db.get_user_cart(call.from_user.id)
    cost = 0
    for item in cart:
        msg += f"\n{item[0]} {item[1]} {item[2]} - {item[3]}₽"
        cost += float(item[3])
    msg += f"\n\nАдрес: {db.get_user_address(call.from_user.id)}"
    if call.data == "cash":
        msg += "\n\nОплата: наличными"
    else:
        msg += "\n\nОплата: по карте"
    global comment
    if comment != "":
        msg += f"\n\nКомментарий пользователя:\n{comment}"
    bot.send_message(config.admin, msg, reply_markup=keyboards.get_delivered_markup(call.from_user.id))


if __name__ == '__main__':
    bot.polling()
