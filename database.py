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

        with open('ddl/minhafacul.sql', 'r') as sql_file:
            sql_script = sql_file.read()

        self.query.executescript(sql_script)
        self.connection.commit()

    def user_exists(self, email: str, password: str) -> bool:

        self.query.execute(f"SELECT * FROM USUARIO WHERE EMAIL == '{email}' AND SENHA_SHA256 == '{password}'")
        logger.info(f"SELECT * FROM USUARIO WHERE EMAIL == '{email}' AND SENHA_SHA256 == '{password}'")

        account = self.query.fetchone()

        if not account:
            return False
        
        return True
    
    def insert_user(self, email: str, password: str, password_c: str, local_txt: str, latitude, longitude, course) -> bool:
        
        if len(email) > 300:
            return False
        elif len(password)> 64:
            return False
        elif password_c != password:
            return False
        elif len(local_txt)> 300:
            return False
                
        self.query.execute(f"INSERT OR IGNORE INTO USUARIO(EMAIL, SENHA_SHA256, LOCAL_TXT, LOCAL_LAT, LOCAL_LON, CURSO_ID) values ('{email}', '{password}', '{local_txt}', {latitude}, {longitude}, {course});")
        logger.info(f"INSERT OR IGNORE INTO USUARIO(EMAIL, SENHA_SHA256, LOCAL_TXT, LOCAL_LAT, LOCAL_LON, CURSO_ID) values ('{email}', '{password}', '{local_txt}', {latitude}, {longitude}, {course});")
        self.connection.commit()
        
        return True
    
    def get_user_email(self, user_id: int) -> str:

        self.query.execute(f"SELECT EMAIL FROM USUARIO WHERE USUARIO_ID == '{user_id}'")
        logger.info(f"SELECT LOCAL_TXT FROM USUARIO WHERE USUARIO_ID == '{user_id}'")

        email = self.query.fetchone()
        return email[0]

    def get_user_local(self, user_id: int) -> str:

        self.query.execute(f"SELECT LOCAL_TXT FROM USUARIO WHERE USUARIO_ID == '{user_id}'")
        logger.info(f"SELECT LOCAL_TXT FROM USUARIO WHERE USUARIO_ID == '{user_id}'")

        local = self.query.fetchone()

        if not local:
            return str()

        return local[0]
    
    def get_user_latitude(self, user_id: int) -> str:

        self.query.execute(f"SELECT LOCAL_LAT FROM USUARIO WHERE USUARIO_ID == '{user_id}'")
        logger.info(f"SELECT LOCAL_LAT FROM USUARIO WHERE USUARIO_ID == '{user_id}'")

        latitude = self.query.fetchone()
        return latitude[0]
    
    def get_user_longitude(self, user_id: int) -> str:

        self.query.execute(f"SELECT LOCAL_LON FROM USUARIO WHERE USUARIO_ID == '{user_id}'")
        logger.info(f"SELECT LOCAL_LON FROM USUARIO WHERE USUARIO_ID == '{user_id}'")

        longitude = self.query.fetchone()
        return longitude[0]
    
    def get_user_course(self, user_id: int) -> str:

        self.query.execute(f"SELECT CURSO_ID FROM USUARIO WHERE USUARIO_ID == '{user_id}'")
        logger.info(f"SELECT CURSO_ID FROM USUARIO WHERE USUARIO_ID == '{user_id}'")

        course_id = self.query.fetchone()
        return course_id[0]
    
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

    def alter_course(self, user_id, course_id):
        self.query.execute(f"UPDATE USUARIO SET CURSO_ID = '{course_id}' WHERE USUARIO_ID == {user_id}")
        logger.info(f"UPDATE USUARIO SET CURSO_ID = '{course_id}' WHERE USUARIO_ID == {user_id}")
        self.connection.commit()

    def is_admin(self, user_id):
        self.query.execute(f"SELECT ADMINISTRADOR FROM USUARIO WHERE USUARIO_ID == {user_id}")
        logger.info(f"SELECT ADMINISTRADOR FROM USUARIO WHERE USUARIO_ID == {user_id}")

        is_admin = self.query.fetchone()
        
        return is_admin[0]

    def get_courses(self):
        self.query.execute("SELECT CURSO_ID, CURSO FROM CURSO")
        cursos = self.query.fetchall()

        return cursos