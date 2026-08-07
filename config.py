import os
from dotenv import load_dotenv


load_dotenv()



# База данных PosgreSQL #
POSTGRESQL_HOST=os.environ["POSTGRESQL_HOST"]
POSTGRESQL_PORT=os.environ["POSTGRESQL_PORT"]
POSTGRESQL_USER=os.environ["POSTGRESQL_USER"]
POSTGRESQL_PASSWORD=os.environ["POSTGRESQL_PASSWORD"]
POSTGRESQL_DBNAME=os.environ["POSTGRESQL_DBNAME"]


# Секретный ключ Flask #
SECRET_KEY=os.environ["SECRET_KEY"]




# Пароль для страницы охраны #
ADMIN_SQ_PASSWORD=os.environ["ADMIN_SQ_PASSWORD"]