import sqlite3
from config import logger
from string import ascii_letters
from error import DB_Error, NonExistingUser, UpdateError
from typing import NamedTuple
import datetime


class Answer(NamedTuple):
    id: int
    data: datetime.datetime | None = None
    user_id: int | None = None
    role: str | None = None
    message: str | None = None
    gpt_tokens: str | None = None
    symbols: int | None = None
    blocks: int | None = None


class Validation:
    correct_symbols = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя-_1234567890' + ascii_letters

    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        self.valid(value)
        instance.__dict__[self.name] = value

    @classmethod
    def valid(cls, item):
        if not isinstance(item, str):
            raise TypeError("Incorrect type of name")
        if item.lower().strip(cls.correct_symbols):
            raise ValueError("Incorrect name."
                             "You can use only ascii letters, russian letters, and -,_ and numbers.")
        return item


class DB:
    non_existing_user = 'Не существующий пользователь.'
    update_error = ''
    db_error = 'Ошибка: '
    db_name = Validation()
    table_name = Validation()

    def __init__(self,
                 db_name: str,
                 table_name: str):
        self.db_name = db_name
        self.table_name = table_name
        self._create_db()
        self._create_table()

    def _create_db(self) -> None:
        con = sqlite3.connect(self.db_name + '.db')
        con.close()

    def _create_table(self) -> None:
        sql_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name}(
        id INT NOT NULL PRIMARY KEY,
        date TEXT NOT NULL,
        user_id INT NOT NULL, 
        role TEXT,    
        message TEXT,
        gpt_tokens INT NOT NULL,
        symbols INT NOT NULL,
        blocks INT NOT NULL       
        );
        """
        self.__connect_to_db(sql_query)

    def update_data(self, id: int,
                    column: str, value: str
                    ) -> None | NonExistingUser:
        if self._is_id_in_db(id):
            self._update_user_in_db(id, column, value)
            return

        self._logger(self.non_existing_user)
        raise NonExistingUser(self.non_existing_user)

    def _is_id_in_db(self, id: int) -> bool:
        sql_query = f'''
            SELECT id
            FROM {self.table_name}
            WHERE id = {id}
            '''
        return bool(self.__connect_to_db(sql_query))

    def _update_user_in_db(self, id: int,
                           column: str, value: str) -> None:
        sql_query = f"""
                    UPDATE {self.table_name}
                    SET {column} = ?
                    WHERE id = {id};
                    """

        self.__connect_to_db(sql_query, (value,))

    def __connect_to_db(self, query: str,
                        data: tuple | None = None
                        ) -> list[Answer] | tuple | DB_Error:
        con = sqlite3.connect(self.db_name + '.db')
        cur = con.cursor()

        try:
            if data:
                cur.execute(query, data)
                con.commit()
            else:
                cur.execute(query)
                con.commit()
        except sqlite3.Error as error:
            self._logger(self.db_error + str(error))
            raise DB_Error(self.db_error + str(error))
        else:
            result = cur.fetchall()
            if result:
                if len(result[0]) == 1:
                    return result[0]

            return [Answer(*result[i]) for i in range(len(result))] \
                if result else tuple()

        finally:
            con.close()

    def select_data(self, user_id: int = 1, is_id: bool = False, id: int = 1
                    ) -> list[Answer] | NonExistingUser | Answer:
        if not is_id:
            if self._user_in_db(user_id):
                sql_query = f'''SELECT * 
                        FROM {self.table_name} 
                        WHERE user_id = {user_id}
                        ORDER BY date DESC'''
                return self.__connect_to_db(sql_query)
            self._logger(self.non_existing_user)
            raise NonExistingUser(self.non_existing_user)
        if self._is_id_in_db(id):
            sql_query = f'''SELECT * 
                        FROM {self.table_name} 
                        WHERE id = {id}
                        ORDER BY date DESC'''
            return self.__connect_to_db(sql_query)[0]
        self._logger(self.non_existing_user)
        raise NonExistingUser(self.non_existing_user)

    def delete_user(self, user_id: int) -> None | NonExistingUser:
        if self._user_in_db(user_id):
            sql_query = f'''
                DELETE
                FROM {self.table_name}
                WHERE user_id = {user_id}
                '''
            self.__connect_to_db(sql_query)
            return
        self._logger(self.non_existing_user)
        raise NonExistingUser(self.non_existing_user)

    def _user_in_db(self, user_id: int) -> bool:
        sql_query = f'''
            SELECT user_id
            FROM {self.table_name}
            WHERE user_id = {user_id}
            '''
        return bool(self.__connect_to_db(sql_query))

    def _last_user_id(self):
        last_user_id = self.__connect_to_db(f'SELECT id '
                                            f'FROM {self.table_name} '
                                            f'ORDER BY id DESC '
                                            f'LIMIT 1;')
        if last_user_id:
            new_id = last_user_id[0] + 1
        else:
            new_id = 1
        return new_id

    def make_new_user(self, user_id: int, roles: str, ) -> None:
        new_id = self._last_user_id()

        sql_query = f"""
                    INSERT INTO {self.table_name}(id, user_id, date, role, gpt_tokens, symbols, blocks)
                    VALUES ({new_id}, {user_id}, datetime('now', 'localtime'), "{roles}", 0, 0, 0);
                    """
        self.__connect_to_db(sql_query)

    @staticmethod
    def _logger(error_msg: str) -> None:
        logger.error(error_msg)


if __name__ == '__main__':
    db = DB('sqlite3', 'users')
    db.make_new_user(11, 'user')
    # data = db.select_data(11)
    # print(data)
    # db.update_data(data[0].id, 'character', 'lox')
    # data = db.select_data(11)
    # print(data)
