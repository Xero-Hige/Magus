import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TaggedTweet(Base):
    __tablename__ = "tweets"

    id = Column(String, primary_key=True)
    joy = Column(Integer, default=0)
    trust = Column(Integer, default=0)
    fear = Column(Integer, default=0)
    surprise = Column(Integer, default=0)
    sadness = Column(Integer, default=0)
    disgust = Column(Integer, default=0)
    anger = Column(Integer, default=0)
    anticipation = Column(Integer, default=0)
    none = Column(Integer, default=0)
    ironic = Column(Integer, default=0)

    totals = Column(Integer, nullable=False)


import os
from sqlalchemy import create_engine

engine = create_engine(
    'postgres://{0}:{1}@horton.elephantsql.com:5432/{0}'.format(os.environ['SQL_USER'], os.environ['SQL_PASS']))

from sqlalchemy.orm import sessionmaker

Session = sessionmaker()
Session.configure(bind=engine)
try:
    Base.metadata.create_all(engine)
except:
    pass


class DB_Handler:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.close()

    def get_tagged(self, tweet_id):
        try:
            tweet = self.session.query(TaggedTweet).filter(TaggedTweet.id == tweet_id).one()
        except sqlalchemy.orm.exc.NoResultFound:
            tweet = None

        if not tweet:
            tweet = TaggedTweet(id=tweet_id, totals=1)
            self.session.add(tweet)
            self.session.commit()

        return tweet

    def get_all_tagged(self):
        try:
            tweets = self.session.query(TaggedTweet)

        except sqlalchemy.orm.exc.NoResultFound:
            tweets = []

        return tweets
