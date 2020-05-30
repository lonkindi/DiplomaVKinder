from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer

Base = declarative_base()
engine = create_engine('postgresql://test:1234@localhost/VKinder')
Session = sessionmaker(bind=engine)
session = Session()


class Candidate(Base):
    __tablename__ = 'candidate'

    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)

    def saveData(self, customer):
        session = Session(bind=self.connection)
        session.add(customer)
        session.commit()


def add_candidate(vk_id, user_id):
    new_candidate = Candidate(vk_id=vk_id, user_id=user_id)
    session.add(new_candidate)
    session.commit()


def get_used(user_id):
    id_list = list()
    res_query = session.query(Candidate).filter(Candidate.user_id == user_id).all()
    for item in res_query:
        id_list.append(item.vk_id)
    return id_list


def create_all():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all()
