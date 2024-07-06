
from .models import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import getenv


class Database:
    __engine = None
    
    def __init__(self):
        load_dotenv()
        # Database credentials
        username = getenv('db_user')
        password = getenv('db_pass')
        host = 'localhost'
        port = '5432'
        database = getenv('db')

        # Create an engine
        self.__engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

    def reload(self):
        # Create the tables
        Base.metadata.create_all(self.__engine)

        # Create a session
        Session = sessionmaker(bind=self.__engine)
        session = Session()
