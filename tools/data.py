import pickle

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from mltool.descriptors import *

Base = declarative_base()


class SearchOperation(Base):
    """
    Describes the results and progress of a single execution of the 
    CalculateApplication.
    """
    __tablename__ = 'spaces'

    # Primary key
    id = Column(Integer, primary_key=True)

    # Serialized search space explored during the calculations.
    space = Column(String)

    # Search space description (used for faster browsing, no need to deserialize 
    # 'space').
    space_descr = Column(String)

    # The highest index of a descriptor pair for which the results have been 
    # calculated.
    latest = Column(Integer)

    # Serialized list of tuples of ranges of indices (less than latest) of 
    # descriptor pairs for which the results haven't been calculated yet. 
    unfinished = Column(String)

    # Should those results be considered by the compare script?
    enabled = Column(Boolean)

    # Have the calculations finished?
    done = Column(Boolean)

    score_entries = relationship('SearchSpaceScore', cascade="all, delete-orphan")


class SearchSpaceScore(Base):
    """
    Stores partial results of calculations.
    """
    __tablename__ = 'scores'

    # Primary key
    id = Column(Integer, primary_key=True)

    # Foreign key
    space_id = Column(Integer, ForeignKey('spaces.id'))

    # Serialized list of tuples (precision, sensivity, f1) of calculation 
    # results.
    scores = Column(String)


class SpaceDataStore(object):
    """
    Facade for working with data stored in the database. The data describes 
    the calculation results and calculation progress.
    """
    def __init__(self, dburl):
        """
        Creates a facade.
        :param dburl: URL to the SQL database (SQLAlchemy syntax).
        """
        engine = create_engine(dburl, echo=False, echo_pool=False)
        SearchOperation.metadata.create_all(engine) 
        self._session_factory = sessionmaker(bind=engine)

    def add_scores(self, space, scores, latest, unfinished):
        """
        Store partial results of the calculation.
        :param space: SearchSpace object explored during calculations.
        :param scores: List of tuples (precision, sensitivity, f1).
        :param latest: Highest index of a description pair for which the 
        results have been calculated.
        :param unfinished: List of tuples describing ranges of indices of 
        descriptor pairs for which the results haven't been calculated yet, 
        indices < latest.
        """
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        if not space_obj:
            space_obj = SearchOperation(space_descr=str(space), space=pickle.dumps(space),
                                        enabled=True, done=False)
            session.add(space_obj)
            session.commit()
        space_obj.latest = latest
        space_obj.unfinished = pickle.dumps(unfinished)

        scores_obj = SearchSpaceScore(space_id=space_obj.id)
        scores_obj.scores = pickle.dumps(scores)
        session.add(scores_obj)
        session.commit()
        session.close()

    def enable(self, id):
        """
        Mark a SearchOperation as enabled.
        :param id: SearchOperation id.
        """
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(id=id).first()
        if space_obj:
            space_obj.enabled = True
            session.commit()
        session.close()

    def disable(self, id):
        """
        Disable a SearchOperation.
        :param id: SearchOperation id
        """
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(id=id).first()
        if space_obj:
            space_obj.enabled = False
            session.commit()
        session.close()

    def is_enabled(self, id):
        """
        Checks if a SearchOperation is enabled.
        :param id: SearchOperation id.
        :returns: True iff it's enabled.
        """
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(id=id).first()
        enabled = False
        if space_obj:
            enabled = space_obj.enabled
        session.close()
        return enabled

    def get_retry_info(self, space):
        """
        Gets data describing the calculation progress. The data can be used to 
        retry the calculations.
        :param space: SearchSpace that the calculations explored.
        :returns: If space exists in the database, a tuple (l, u) where l is 
        SearchOperation latest and u is a list of all unfinished work indices.
        If space doesn't exist in the database, None is returned.
        """
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        result = None
        if space_obj:
            result = (space_obj.latest, pickle.loads(space_obj.unfinished))
        session.close()
        return result

    def mark_done(self, space):
        """
        Marks a SearchOperation as done. 
        :param space: SearchSpace of SearchOperation to mark.
        """
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        space_obj.done = True
        session.commit()
        session.close()

    def isdone(self, space):
        """
        Check if calculations for a SearchOperation are finished.
        :param space: SearchSpace of SearchOperation to check.
        :returns: True if the operation finished, False if it didn't or it 
        doesn't exist.
        """
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        is_done = False
        if space_obj:
            is_done = space_obj.done
        session.close()
        return is_done

    def get_spaces(self, require_enabled=False):
        """
        Return all SearchSpaces in the database.
        :param require_enabled: If True, only spaces of enabled SearchOperations 
        will be returned.
        :returns: List of spaces.
        """
        session = self._session_factory()
        if require_enabled:
            objects = session.query(SearchOperation).filter_by(enabled=True).order_by(SearchOperation.id).all()
        else:
            objects = session.query(SearchOperation).order_by(SearchOperation.id).all()
        result = [pickle.loads(obj.space) for obj in objects]
        session.close()
        return result

    def get_scores(self, space=None, id=-1):
        """
        Returns all score tuples for a given SearchOperation. The operation 
        can be chosen by its SearchSpace or by its id.
        :param space: SearchOperation SearchSpace.
        :param id: SearchOperation id.
        :returns: List of tuples (precision, sensitivity, f1).
        """
        session = self._session_factory()
        if space:
            space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        else:
            space_obj = session.query(SearchOperation).filter_by(id=id).first()
        result = self._get_scores_from_children(space_obj)
        session.close()
        return result

    def delete(self, space):
        """
        Deletes an operation from the database.
        :param space: SearchSpace of an operation to delete.
        """
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        if space_obj:
            session.delete(space_obj)
            session.commit()
        session.close()

    def get_id(self, space):
        """
        Get id of a SearchOperation by specifying its SearchSpace.
        :param space: SearchSpace of an operation
        :returns: Operations id.
        """
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        id = False
        if space_obj:
            id = space_obj.id
        session.close()
        return id

    def _get_scores_from_children(self, obj):
        total_scores = []
        for score_obj in obj.score_entries:
            total_scores.extend(pickle.loads(score_obj.scores))
        return total_scores
