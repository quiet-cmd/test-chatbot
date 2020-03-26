# -*- coding: utf-8 -*-
import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def all_table_name(self):
        """ Получаем все имена таблиц """
        with self.connection:
            return self.cursor.execute('SELECT name from sqlite_master where type= "table"').fetchall()

    def select_all(self, table_name):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM  {0}'.format(table_name[0])).fetchall()

    def select_single(self, table_name, rownum):
        """ Получаем одну строку с номером rownum """
        with self.connection:
            return self.cursor.execute('SELECT * FROM {0} WHERE id = ?'.format(table_name[0]), (rownum,)).fetchall()[0]

    def count_rows(self, table_name):
        """ Считаем количество строк """
        with self.connection:
            result = self.cursor.execute('SELECT * FROM {0}}'.format(table_name[0])).fetchall()
            return len(result)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
