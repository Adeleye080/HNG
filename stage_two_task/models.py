from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String


# Define the Base class
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    userId = Column(Integer, primary_key=True, nullable=False, unique=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    phone = Column(String)

    def __repr__(self):
        return f"<User(name='{self.name}', age={self.age})>"
    
    def to_dict(self):
        """
        convert object to dictionary
        """
        dic = dict(self.__dict__)
        if '_sa_instance_state' in dic:
            del dic['_sa_instance_state']
        if 'password' in dic:
            del dic['password']
            
        return dic
    
