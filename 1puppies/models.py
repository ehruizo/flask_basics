from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


engine = create_engine('sqlite:///puppies.db')
Base = declarative_base()
Base.metadata.bind = engine


class Puppy(Base):
    __tablename__ = 'puppy'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id, 'name': self.name, 'description': self.description}


def init_db():
    Base.metadata.create_all(engine)
