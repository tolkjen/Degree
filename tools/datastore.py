from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

Base = declarative_base()


class SearchOperation(Base):
    __tablename__ = 'operations'

    space = Column(String, primary_key=True)
    result = Column(String)
    latest = Column(Integer)
    done = Column(Boolean)

    def __repr__(self):
        return '<SearchOperation(space=%s, done=%s, latest=%d, result=%s)>' % (
            self.space, self.done, self.latest, self.result)


class DataStore(object):
    def __init__(self, url):
        engine = create_engine(url, echo=False, poolclass=QueuePool)
        SearchOperation.metadata.create_all(engine) 
        self._session_factory = sessionmaker(bind=engine)

    def set(self, space, result, latest, done=False):
        session = self._session_factory()
        operation = session.query(SearchOperation).filter_by(space=space).first()
        if not operation:
            operation = SearchOperation(space=space)
            session.add(operation)
        operation.result = result
        operation.latest = latest
        operation.done = done
        session.commit()

    def is_done(self, space):
        session = self._session_factory()
        operation = session.query(SearchOperation).filter_by(space=space).first()
        if operation:
            return operation.done
        return False

    def get_latest(self, space):
        session = self._session_factory()
        operation = session.query(SearchOperation).filter_by(space=space).first()
        if not operation:
            raise Exception('Space %s not in data store!' % space)
        return operation.latest

    def remove(self, space):
        session = self._session_factory()
        operation = session.query(SearchOperation).filter_by(space=space).first()
        if operation:
            session.delete(operation)
            session.commit()


if __name__ == '__main__':  
    store = DataStore('sqlite:///data.db')
    store.set('s', 'r', 0, False)
    store.set('s', 'r', 123, True)
    print store.get_latest('s')
    print store.is_done('s')
