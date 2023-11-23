from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.future import select
from datetime import datetime

from migrations.database import Base, db

from uuid import uuid4

class User():
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    discord_id = Column(Text)
    server_id = Column(Text)
    name = Column(Text)

class Rating():
    __tablename__ = 'rating'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.id'))
    rating = Column(BigInteger)
    type = Column(Text)

class Match():
    __tablename__ = 'match'

    id = Column(BigInteger, primary_key=True)
    played_timestamp = Column(DateTime)

class Player():
    __tablename__ = 'player'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.id'))
    user_id = Column(BigInteger, ForeignKey('match.id'))
    result = Column(Text)