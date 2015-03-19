from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
import pickle
from mltool.spaces import *
from mltool.descriptors import *

Base = declarative_base()


class SearchOperation(Base):
    __tablename__ = 'operations'

    space = Column(String, primary_key=True)
    result = Column(String)
    latest = Column(Integer)
    done = Column(Boolean)
    ranges = Column(String)

    def __repr__(self):
        return '<SearchOperation(space=%s, done=%s, latest=%d, result=%s)>' % (
            self.space, self.done, self.latest, self.result)


class DataStore(object):
    def __init__(self, url):
        engine = create_engine(url, echo=False, echo_pool=False)
        SearchOperation.metadata.create_all(engine) 
        self._session_factory = sessionmaker(bind=engine)

    def set(self, space, result, latest, done=False, ranges=[]):
        session = self._session_factory()
        operation = session.query(SearchOperation).filter_by(space=space).first()
        if not operation:
            operation = SearchOperation(space=space)
            session.add(operation)
        operation.result = pickle.dumps(result)
        operation.latest = latest
        operation.done = done
        operation.ranges = pickle.dumps(ranges)
        session.commit()

    def is_done(self, space):
        session = self._session_factory()
        operation = session.query(SearchOperation).filter_by(space=space).first()
        if operation:
            return operation.done
        return False

    def get_all(self):
        session = self._session_factory()
        return session.query(SearchOperation).all()

    def get_latest(self, space):
        session = self._session_factory()
        operation = session.query(SearchOperation).filter_by(space=space).first()
        if not operation:
            return None
        return operation.latest

    def get_result(self, space):
        session = self._session_factory()
        operation = session.query(SearchOperation).filter_by(space=space).first()
        if not operation:
            raise Exception('Space %s not in data store!' % space)
        return pickle.loads(operation.result)

    def get_ranges(self, space):
        session = self._session_factory()
        operation = session.query(SearchOperation).filter_by(space=space).first()
        if not operation:
            raise Exception('Space %s not in data store!' % space)
        return pickle.loads(operation.ranges)

    def remove(self, space):
        session = self._session_factory()
        operation = session.query(SearchOperation).filter_by(space=space).first()
        if operation:
            session.delete(operation)
            session.commit()


if __name__ == '__main__':  
    store = DataStore('sqlite:///cache.db')

    print ''
    for op in store.get_all():
        result, descriptor_pair = pickle.loads(op.result)

        print 'SPACE:  ', op.space
        print 'RESULT: ', result
        print 'DESCR:  ', descriptor_pair
        print 'RANGES: ', pickle.loads(op.ranges)
        print 'DONE:    %s (Latest = %d)' % (op.done, op.latest)
        print ''
