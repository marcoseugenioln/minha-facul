import sqlite3
import logging

logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('site-log.log')
logger.addHandler(handler)

class Database():

    def __init__(self):
        logger.info('starting database connection')
        connection = sqlite3.connect('minhafacul.db', check_same_thread=False, timeout=10)
        self.query = connection.cursor()
        logger.info('Database connected.')

    

    def user_exists(self, email: str, password: str) -> bool:

        self.query.execute(f"SELECT * FROM USUARIO WHERE EMAIL == '{email}' AND SENHA_SHA256 == '{password}'")

        account = self.query.fetchone()

        if not account:
            return False
        
        return True
    
    def insert_user(self, email: str, password: str, local_txt: str) -> bool:
        
        if len(email) > 300:
            return False
        elif len(password)> 64:
            return False
        elif len(password)> 300:
            return False
                
        self.query.execute(f"INSERT INTO USUARIO(EMAIL, SENHA_SHA256, LOCAL_TXT) values ('{email}', '{password}', '{local_txt}');")
        logger.info(f"INSERT INTO USUARIO(EMAIL, SENHA_SHA256, LOCAL_TXT) values ('{email}', '{password}', '{local_txt}');")

        return True


