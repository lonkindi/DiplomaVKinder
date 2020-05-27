from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, String, Integer, Date, Boolean

Base = declarative_base()
engine = create_engine('postgresql://test:1234@localhost/VKinder')
Session = sessionmaker(bind=engine)
session = Session()


class Candidate(Base):
    __tablename__ = 'candidate'

    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)
    # used = Column(Boolean)
    # m_friends = Column(Boolean)
    # m_groups = Column(Boolean)
    # interests = Column(String)
    # music = Column(String)
    # books = Column(String)
    # photos = Column(JSONB, default=list)

    # name = Column(String(250), nullable=False)
    # start_at = Column(Date, nullable=False)
    # item = Column(JSONB, default=list, nullable=False)

    def saveData(self, customer):
        session = Session(bind=self.connection)
        session.add(customer)
        session.commit()


def add_candidate(vk_id, user_id): #, used=False, m_friends=False, m_groups=False, interests='', music='', books='', photos=[]):
    new_candidate = Candidate(vk_id=vk_id, user_id=user_id) #, used=used, m_friends=m_friends, m_groups=m_groups, interests=interests,
                           # music=music, books=books, photos=photos)
    session.add(new_candidate)
    session.commit()

def get_used(user_id):
    id_list = list()
    res_query = session.query(Candidate).filter(Candidate.user_id==user_id).all()
    for item in res_query:
        id_list.append(item.vk_id)
    return id_list


def create_all():
    '''Создать все таблицы в БД'''
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    # create_all()

    # add_candidate(vk_id=10754162, user_id=24863449)

    print(get_used(24863449))


    # item = {'id': 24863449, 'first_name': 'Дмитрий', 'last_name': 'Лонкин', 'is_closed': False,
    #         'can_access_closed': True,
    #         'sex': 2, 'bdate': '26.12.1976', 'city': {'id': 106, 'title': 'Оренбург'}, 'interests': 'IT, АСУ',
    #         'music': 'вся, которая нравится', 'movies': '', 'books': 'С.Кинг, Вербер', 'games': 'Преферанс'}
    # id = 24863449
    # add_friend(item)
