import sqlite3
import logging

logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('site-log.log')
logger.addHandler(handler)

class Database():

    

    def __init__(self):
        print('starting database...')
        connection = sqlite3.connect('database.db', check_same_thread=False, timeout=10)
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
    
    def insert_user(self, username: str, password: str, city: str, state: str) -> bool:
        
        if len(username) > 20:
            return False
        elif len(password)> 20:
            return False
        elif len(city)> 20:
            return False
        elif len(state)> 20:
            return False
        
        self.query.execute(f"INSERT INTO users(username, password, city, state) values ('{username}', '{password}', '{city}', '{state}');")
        
        logger.info(f"INSERT INTO users(username, password, city, state) values ('{username}', '{password}', '{city}', '{state}')")
        return True


