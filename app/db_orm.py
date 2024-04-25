from os import getenv
from sqlalchemy import create_engine, Column, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection
SQLALCHEMY_DATABASE_URL = getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the base class
Base = declarative_base()


class Preferences (Base):
    """ Define the preferences table """
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)


def create_preferences_table():
    """ Create the preferences table """
    Base.metadata.create_all(bind=engine)


def get_preferences_number_of_rows():
    try:
        session = SessionLocal()
        result = session.query(Preferences).count()
        session.close()
        return result
    except Exception as e:
        return None


def get_preferences_by_user_id(user_id: int):
    """ Get the preferences by user id.
        If the user does not exist, return None."""
    session = SessionLocal()
    preferences = session.query(Preferences).filter(Preferences.id == user_id).first()
    session.close()
    return preferences


def upsert_preferences(user_id: int, email_enabled: bool, sms_enabled: bool):
    """ Update or insert the preferences """
    session = SessionLocal()
    preferences = session.query(Preferences).filter(Preferences.id == user_id).first()
    if preferences is None:
        preferences = Preferences(id=user_id, email_enabled=email_enabled, sms_enabled=sms_enabled)
        session.add(preferences)
    else:
        preferences.email_enabled = email_enabled
        preferences.sms_enabled = sms_enabled
    session.commit()
    session.refresh(preferences)
    session.close()
    return preferences
