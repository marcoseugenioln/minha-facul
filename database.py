import sqlite3

class Database():

    def __init__(self):
        print('starting database...')
        connection = sqlite3.connect('database.db', check_same_thread=False)
        self.query = connection.cursor()
        
    def create_users_table(self):
        print('creating users tables...')
        self.query.execute(
            '''
            CREATE TABLE IF NOT EXISTS 
            users(
                user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                username VARCHAR(20), 
                password VARCHAR(20), 
                city  VARCHAR(20),
                state  VARCHAR(20)
            )
            ''')

    def user_exists(self, username: str, password: str) -> bool:

        self.query.execute(f"SELECT * FROM users WHERE username == '{username}' AND password == '{password}'")

        account = self.query.fetchone()

        if not account:
            return False
        
        return True
