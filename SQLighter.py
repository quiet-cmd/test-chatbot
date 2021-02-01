# -*- coding: utf-8 -*-
import sqlite3


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_all_table_name(self):
        with self.connection:
            return [i[0] for i in self.cursor.execute('SELECT name from sqlite_master where type= "table"').fetchall()]

    def get_all_table_rows(self, table_name):
        with self.connection:
            return self.cursor.execute(f'SELECT * FROM  {table_name}').fetchall()

    def close(self):
        self.connection.close()
