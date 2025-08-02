import sqlite3


class BotDB:

    def __init__(self, db_file):  # Функция, автоматически срабатываемая при запуске
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_new_order(self, user_id):
        self.cursor.execute(f"INSERT INTO `cart` (`user_id`) VALUES ({user_id})")
        return self.conn.commit()

    # Проверяем, есть ли номер телефона в базе
    def check_phone_number(self, number):
        result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `phone_number` = ?", (number,))
        return result.fetchone()

    # Получаем адрес зарегестрированного пользователя
    def get_user_address(self, user_id):
        result = self.cursor.execute("SELECT `address` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    # Добавляем нового клиента в базу
    def add_new_user(self, user_id, first_name, last_name, phone_number):
        self.cursor.execute("INSERT INTO `users` (`user_id`, `first_name`, `last_name`, `phone_number`) "
                            "VALUES (?, ?, ?, ?)",
                            (user_id, first_name, last_name, phone_number))
        return self.conn.commit()

    # Вводим/изменяем адрес пользователя
    def set_address(self, user_id, address):
        self.cursor.execute('UPDATE users SET address = ?  where user_id = ?', (address, user_id))
        return self.conn.commit()

    # Получить категории блюд
    def get_categories(self):
        result = self.cursor.execute(f"SELECT `name`, `callback_data` FROM `categories`")
        return result.fetchall()

    # Получить вкусы категории
    def get_tastes(self, category):
        result = self.cursor.execute(f"SELECT food.name, food.callback_data FROM `food` JOIN `categories` on "
                                     f"food.category_id = categories.id WHERE categories.callback_data = \"{category}\"")
        return result.fetchall()

    def get_all_food(self):
        result = self.cursor.execute("SELECT name, description, photo, callback_data FROM food")
        return result.fetchall()

    def get_category_callbacks(self):
        return [category[1] for category in self.get_categories()]

    def get_subcategory_callbacks(self, callback):
        return [category[1] for category in self.get_tastes(callback)]

    # Получить callback.data категории определенного вида
    def get_category_of_food(self, food_name):
        result = self.cursor.execute(f"SELECT categories.callback_data FROM `food` "
                                     f"JOIN `categories` on food.category_id = categories.id "
                                     f"WHERE food.callback_data = \"{food_name}\"")
        return result.fetchone()[0]

    def get_food_info(self, callback):
        result = self.cursor.execute(f"SELECT food.name, food_price.price, food_price.weight, food_price.unit, "
                                     f"food.callback_data, food.description, food.photo"
                                     f" FROM `food` JOIN `food_price` on food_price.food_id = food.id "
                                     f"WHERE food.callback_data = \"{callback}\"")
        return result.fetchall()

    def get_food_callbacks(self):
        result = self.cursor.execute("SELECT food.callback_data FROM food")
        return [item[0] for item in result]

    def add_to_cart(self, user_id, name, count):
        result = self.cursor.execute(f"INSERT INTO `cart` (user_id, food_id) VALUES ({user_id}, "
                                     f"(SELECT food_price.id FROM `food_price` "
                                     f"JOIN `food` on food_price.food_id = food.id "
                                     f"WHERE food.callback_data = \"{name}\" AND food_price.weight = \"{count}\"))")
        return self.conn.commit()

    def get_user_cart(self, user_id):
        result = self.cursor.execute(f"SELECT name, weight, unit, price, callback_data FROM `food` "
                                     f"JOIN food_price ON food.id = food_price.food_id "
                                     f"JOIN `cart` ON cart.food_id = food_price.id "
                                     f"WHERE cart.user_id = {user_id}")
        return result.fetchall()

    def delete_from_cart(self, user_id, callback_data, weight):
        result = self.cursor.execute(f"DELETE FROM `cart` WHERE id IN "
                                     f"(SELECT cart.id FROM `cart` "
                                     f"JOIN `food_price` ON food_price.id = cart.food_id "
                                     f"JOIN `food` ON food.id = food_price.food_id "
                                     f"WHERE food.callback_data = \"{callback_data}\" "
                                     f"AND cart.user_id = {user_id} "
                                     f"AND food_price.weight = {weight} limit 1)")
        self.conn.commit()

    def clear_cart(self, user_id):
        self.cursor.execute(f"DELETE FROM `cart` WHERE user_id = {user_id}")
        self.conn.commit()

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()
