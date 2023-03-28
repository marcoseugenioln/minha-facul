import sqlite3

class Database():

    def __init__(self):
        print('starting database...')
        connection = sqlite3.connect('database.db')
        self.query = connection.cursor()
        

    def create_tables(self):
        print('creating tables...')
        self.query.execute('CREATE TABLE table')