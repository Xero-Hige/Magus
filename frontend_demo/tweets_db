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

    totals = Column(Integer, nullable=False)


import os
from sqlalchemy import create_engine

engine = create_engine(
    'postgres://{0}:{1}@horton.elephantsql.com:5432/{0}'.format(os.environ[''], os.environ['SQL_PASS']))

from sqlalchemy.orm import sessionmaker

session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)


class DB_Handler:
    def __init__(self):
        self.session = sessionmaker()
        self.session.configure(bind=engine)
        self.s = session()

    def get_tagged(self, tweet_id):
        tweet = self.s.query(TaggedTweet).filter(TaggedTweet.id == tweet_id).one()

        if not tweet:
            tweet = TaggedTweet(id=tweet_id, totals=1)
            self.s.add(tweet)
            self.s.commit()

        return tweet

    def commit_changes(self):
        self.s.commit()
