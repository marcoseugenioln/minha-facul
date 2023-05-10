import sqlite3
import logging

logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('site-log.log')
logger.addHandler(handler)

class Database():

    def __init__(self):
        logger.info('starting database connection')
        self.connection = sqlite3.connect('minhafacul.db', check_same_thread=False, timeout=10)
        self.query = self.connection.cursor()
        logger.info('Database connected.')

    def user_exists(self, email: str, password: str) -> bool:

        self.query.execute(f"SELECT * FROM USUARIO WHERE EMAIL == '{email}' AND SENHA_SHA256 == '{password}'")
        logger.info(f"SELECT * FROM USUARIO WHERE EMAIL == '{email}' AND SENHA_SHA256 == '{password}'")

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
                
        self.query.execute(f"INSERT OR IGNORE INTO USUARIO(EMAIL, SENHA_SHA256, LOCAL_TXT) values ('{email}', '{password}', '{local_txt}');")
        logger.info(f"INSERT OR IGNORE INTO USUARIO(EMAIL, SENHA_SHA256, LOCAL_TXT) values ('{email}', '{password}', '{local_txt}');")
        self.connection.commit()
        
        return True
    
    def get_user_email(self, user_id: int) -> str:

        self.query.execute(f"SELECT EMAIL FROM USUARIO WHERE USUARIO_ID == '{user_id}'")
        logger.info(f"SELECT LOCAL_TXT FROM USUARIO WHERE USUARIO_ID == '{user_id}'")

        email = self.query.fetchone()
        return email

    def get_user_local(self, user_id: int) -> str:

        self.query.execute(f"SELECT LOCAL_TXT FROM USUARIO WHERE USUARIO_ID == '{user_id}'")
        logger.info(f"SELECT LOCAL_TXT FROM USUARIO WHERE USUARIO_ID == '{user_id}'")

        local = self.query.fetchone()

        if not local:
            return str()

        return local
    
    def get_user_id(self, email: str, password: str):

        self.query.execute(f"SELECT USUARIO_ID FROM USUARIO WHERE EMAIL == '{email}' AND SENHA_SHA256 == '{password}'")
        logger.info(f"SELECT USUARIO_ID FROM USUARIO WHERE EMAIL == '{email}' AND SENHA_SHA256 == '{password}'")

        user_id = self.query.fetchone()

        logger.info(f"user_id:{user_id}")
        
        return user_id[0]
    
    def alter_password(self, user_id, password):
        self.query.execute(f"UPDATE USUARIO SET SENHA_SHA256 = '{password}' WHERE USUARIO_ID == {user_id}")
        logger.info(f"UPDATE USUARIO SET SENHA_SHA256 = '{password}' WHERE USUARIO_ID == {user_id}")
        self.connection.commit()

    def alter_local(self, user_id, local):
        self.query.execute(f"UPDATE USUARIO SET LOCAL_TXT = '{local}' WHERE USUARIO_ID == {user_id}")
        logger.info(f"UPDATE USUARIO SET LOCAL_TXT = '{local}' WHERE USUARIO_ID == {user_id}")
        self.connection.commit()

    def alter_email(self, user_id, email):
        self.query.execute(f"UPDATE USUARIO SET EMAIL = '{email}' WHERE USUARIO_ID == {user_id}")
        logger.info(f"UPDATE USUARIO SET EMAIL = '{email}' WHERE USUARIO_ID == {user_id}")
        self.connection.commit()
