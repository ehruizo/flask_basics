from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context


engine = create_engine('sqlite:///bagelShop.db')
Base = declarative_base()
Base.metadata.bind = engine


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    @property
    def serialize(self):
        return {"id": self.id, "user_name": self.username}


class Bagel(Base):
    __tablename__ = 'bagel'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    picture = Column(String)
    description = Column(String)
    price = Column(String)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'code': self.id,
            'name': self.name,
            'picture': self.picture,
            'description': self.description,
            'price': self.price
        }


def init_db():
    Base.metadata.create_all(engine)
