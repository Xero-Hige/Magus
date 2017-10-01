import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from libs.sentiments_handling import *

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

    def get_emotions_list(self):
        """Retuns a list of the emotions in the tweet as a tuple with the format
        (<percentage>,<emotion name>)"""
        emotions = [[self.joy / self.totals, JOY],
                    [self.trust / self.totals, TRUST],
                    [self.fear / self.totals, FEAR],
                    [self.surprise / self.totals, SURPRISE],
                    [self.sadness / self.totals, SADNESS],
                    [self.disgust / self.totals, DISGUST],
                    [self.anger / self.totals, ANGER],
                    [self.anticipation / self.totals, ANTICIPATION],
                    [self.none / self.totals, NONE],
                    [self.none / self.totals, NONE]]

        emotions.sort(reverse=True)

        normalized_value = len(emotions)
        for i, emotion in enumerate(emotions):
            if emotion[0] == 0:
                normalized_value = 0

            must_reduce = i < len(emotions) - 1 and emotions[i][0] != emotions[i + 1][0]

            emotion[0] = normalized_value

            if must_reduce:
                normalized_value = len(emotions) - (i + 1)

            emotions[i] = tuple(emotion)

        return emotions

    def get_sentiment_list(self):

        emotions = self.get_emotions_list()

        results = [(get_sentiment(emotions[i], emotions[j]), (emotions[i][0] + emotions[j][0]) / 2)
                   for i in range(len(emotions))
                   for j in range(i + 1, len(emotions))
                   if get_sentiment(emotions[i], emotions[j])
                   if emotions[i][0] != 0 and emotions[j][0] != 0
                   # Padding at the end
                   ] + [("-", 0)] * 5

        results.sort(reverse=True, key=lambda x: x[1])

    def get_groups_percent(self):
        total = {HAPPY: 0, SAD: 0, ANGRY: 0, NONE: 0}
        acum = 0

        for sentiment in:
            total[GROUPS.get(sentiment[0], NONE)] += sentiment[1]
            acum += sentiment[1]

        if acum == 0:
            return total

        for sentiment in total:
            total[sentiment] /= acum
            total[sentiment] *= 100

        return total


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
