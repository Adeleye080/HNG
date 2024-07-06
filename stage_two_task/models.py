from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, ForeignKey, Table
from uuid import uuid4
import bcrypt


# Define the Base class
Base = declarative_base()


# many to many relationship association table between organization and users
user_organizations = Table('user_organizations', Base.metadata,
                           Column('user_id', String, ForeignKey(
                               'users.userId'), primary_key=True, nullable=False),
                           Column('organization_id', String, ForeignKey(
                               'organizations.orgId'), primary_key=True, nullable=False)
                           )


# user class
class User(Base):
    __tablename__ = 'users'

    userId = Column(String, primary_key=True, nullable=False, unique=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    phone = Column(String)
    organizations = relationship(
        'Organization', secondary=user_organizations, backref='users')

    def __init__(self, *args, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                if key != '__class__':
                    setattr(self, key, value)
            if 'userId' not in kwargs:
                self.userId = str(uuid4())
            if 'password' in kwargs:
                self.password = bcrypt.hashpw(kwargs['password'].encode(
                    'utf-8'), bcrypt.gensalt()).decode('utf-8')

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

    def save(self):
        """
        save user to database
        """
        from db import storage
        storage.save(self)

    # password_string: str, hashed_password: bytes) -> bool:
    def check_password(self, password_string):
        """
        validates password
        """
        if isinstance(password_string, str):
            return bcrypt.checkpw(password_string.encode('utf-8'), self.password.encode('utf8'))


class Organization(Base):
    __tablename__ = 'organizations'

    orgId = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    description = Column(String)

    def __init__(self, *args, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                if key != '__class__':
                    setattr(self, key, value)
            if 'orgId' not in kwargs:
                self.orgId = str(uuid4())

    def __repr__(self):
        return f"<Organization(name='{self.name}')>"

    def to_dict(self):
        """
        convert object to dictionary
        """
        dic = dict(self.__dict__)
        if '_sa_instance_state' in dic:
            del dic['_sa_instance_state']

        return dic

    def save(self):
        """
        save org to database
        """
        from db import storage
        storage.save(self)
