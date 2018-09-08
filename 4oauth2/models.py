from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random
import string
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired


engine = create_engine('sqlite:///usersWithOAuth.db')
Base = declarative_base()
Base.metadata.bind = engine

secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=6000):
        s = TimedJSONWebSignatureSerializer(secret_key, expires_in=expiration)
        token = s.dumps({'id': self.id})
        return token

    @staticmethod
    def verify_auth_token(token):
        s = TimedJSONWebSignatureSerializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None, True
        except BadSignature:
            return None, False
        user_id = data['id']
        return user_id, False

    @property
    def serialize(self):
        return {"id": self.id, "user_name": self.username, "email": self.email}


def init_db():
    Base.metadata.create_all(engine)

