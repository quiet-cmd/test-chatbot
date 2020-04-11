# -*- coding: utf-8 -*-
import sqlite3


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def all_table_name(self):
        """ Получаем все имена таблиц """
        with self.connection:
            return [i[0] for i in self.cursor.execute('SELECT name from sqlite_master where type= "table"').fetchall()]

    def select_all(self, table_name):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute(f'SELECT * FROM  {table_name}').fetchall()

    def select_question(self, table_name, rownum):
        """ Получаем получаем вопрос с  номером rownum """
        with self.connection:
            result = self.cursor.execute(f'SELECT question FROM {table_name} WHERE id = {rownum}').fetchall()[0]
            return result[0]

    def select_right_answer(self, table_name, rownum):
        """ Получаем правильый ответ  с номером rownum """
        with self.connection:
            result = self.cursor.execute(f'SELECT right_answer FROM {table_name} WHERE id = {rownum}').fetchall()[0]
            return result[0]

    def select_wrong_answers(self, table_name, rownum):
        """ Получаем неправильные ответы  с номером rownum """
        with self.connection:
            result = self.cursor.execute(f'SELECT wrong_answers FROM {table_name} WHERE id = {rownum}').fetchall()[0]
            return result[0]

    def count_rows(self, table_name):
        """ Считаем количество строк """
        with self.connection:
            result = self.cursor.execute(f'SELECT * FROM {table_name}').fetchall()
            return len(result)

    def close(self):
        """ Закрываем текущее соединение с БД  """
        self.connection.close()

    def insert_row(self, num, answer, index):
        """ Обновляет таблицу, если обновленно 0 строк, то записываем строку в БД-хранилище  """
        with self.connection:
            self.cursor.execute(
                f"UPDATE all_answers set answer = '{answer}'  WHERE id == {num} and question_number == {index}")
            if self.cursor.rowcount == 0:
                self.cursor.execute(
                    f"INSERT INTO all_answers (id, answer, question_number) VALUES {num, answer, index}")

    def number_of_correct_answers(self, num):
        """Достаем все ответы пользователя по id поста и складываем ответы"""
        with self.connection:
            result = self.cursor.execute(
                f"SELECT SUM(answer) FROM all_answers WHERE id == {num}").fetchall()[0]
            return result[0]

    def delete_rows(self, num):
        """Удаляет все строки с id равным num"""
        with self.connection:
            self.cursor.execute(f"DELETE FROM all_answers WHERE id = {num}")
