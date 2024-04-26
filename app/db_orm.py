from os import getenv
from sqlalchemy import create_engine, Column, Integer, Boolean, String
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

# This is the users table to mock the users database
class Users (Base):
    """ Define the users table """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)

# This is the properties table to mock the properties database
class Properties (Base):
    """ Define the properties table """
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer, index=True)

def create_preferences_table():
    """ Create tables """
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


create_preferences_table()


### Mocking users and properties tables ###

# Fill the user table with some data to mock the users data
def fill_users_table():
    session = SessionLocal()
    # drop table
    session.query(Users).delete()
    # add new data
    session.add(Users(id=1, email="jhon@gmail.com", phone="555-123-4567"))
    session.add(Users(id=2, email="bob@gmail.com", phone="555-234-4567"))
    session.add(Users(id=3, email="mac@gmail.com", phone="555-345-4567"))
    session.commit()
    session.close()

def get_user_number_of_rows():
    try:
        session = SessionLocal()
        result = session.query(Users).count()
        session.close()
        return result
    except Exception as e:
        return None

def get_users_email_and_phone():
    """ Get the users email and phone."""
    session = SessionLocal()
    user = session.query(Users).all()
    session.close()
    return user

def fill_properties_table():
    session = SessionLocal()
    # drop table
    session.query(Properties).delete()
    # add new data
    session.add(Properties(id=1, name="house", price=100000))
    session.add(Properties(id=2, name="apartment", price=50000))
    session.add(Properties(id=3, name="office", price=200000))
    session.commit()
    session.close()

def get_properties_number_of_rows():
    try:
        session = SessionLocal()
        result = session.query(Properties).count()
        session.close()
        return result
    except Exception as e:
        return None

def get_properties():
    """ Get the properties name and price."""
    session = SessionLocal()
    properties = session.query(Properties).all()
    session.close()
    return properties

def inner_join_users_preferences():
    session = SessionLocal()
    result = session.query(Preferences, Users).filter(Preferences.id == Users.id).all()
    session.close()
    return result

fill_users_table()
fill_properties_table()
