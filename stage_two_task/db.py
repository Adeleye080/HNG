
from models import User, Organization
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import getenv


class Database:
    __engine = None
    __session = None
    
    _entity_mapping = {
        'user': User,
        'org': Organization,
    }

    def __init__(self):
        load_dotenv()
        # Database credentials
        username = getenv('db_user')
        password = getenv('db_pass')
        host = getenv('db_host')
        port = getenv('db_port')
        database = getenv('db')

        # Create an engine
        self.__engine = create_engine(
            f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}', pool_pre_ping=True)

    def reload(self):
        # Create the tables
        from models import Base
        Base.metadata.create_all(self.__engine)

        # Create a session
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()

    def save(self, obj):
        """ save object to database """
        self.__session.add(obj)
        self.__session.commit()
        
        
    def close(self):
        """ close database session """
        self.__session.close()

    def get_one(self, obj: str, filter: dict):
        """ get data from database """
        try:
            obj = self._entity_mapping.get(obj.lower())
            q = self.__session.query(obj).filter_by(**filter).first()
        except Exception:
            return None
        
        return q



storage = Database()
