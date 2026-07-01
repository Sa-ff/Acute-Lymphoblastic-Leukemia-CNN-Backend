#Creates a connection to SQLite and defines the SQLAlchemy Base.
#Initializes tables once at startup.

# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
#from typing import Generator            

DATABASE_URL = "sqlite:///./sdpapp_database.db" #specifying we are using sqlite and the db's relative path # //// four slash for absolute path

#engine is the main connection point to our database
#FastAPI runs many different threads, SQL can only run one thread at a time unless we specify otherwise
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) 

#to prevent from autoinputting data, to prevent it from reloading, then binding our engine with our session 
"""
autocommit=False #we have to explicitly use db.commit() to save a change so that You control exactly when changes become permanent (safety feature)

autoflush=False # Queries only show committed data (Predictability), if e uncommitted changes temporarily appear in queries, it will cause confusion 
bind=engine :  This connects all sessions to our SQLite database
# When we create a session:
db = SessionLocal()  # This session now talks to sdpapp_database.db cus of the bind

"""
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() #base class that we can start building our database model 


# Dependency for FastAPI routes
def get_db(): 
    db = SessionLocal() # Gets a connection FROM THE POOL # This session now talks to sdpapp_database.db
    try:
        yield db # Thread uses its dedicated connection 
    finally:
        db.close() # Returns connection BACK TO POOL

""" note: 

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, pool_size=5)
#SQLite by default only allows the same thread that created the database connection to use it
#FastAPI creates multiple threads to handle multiple requests simultaneously

#when "check_same_thread": False is NOT there
# User A makes request → Thread 1 tries to use database connection created by main thread
# ERROR! SQLite blocks this because different thread is trying to use the connection

#when "check_same_thread": False is there
# User A makes request → Thread 1 uses database ✓  → gets connection #1 from pool
# User B makes request → Thread 2 uses database ✓ → gets connection #2 from pool
# All can use the same database connection from different threads

#check_same_thread=False = Disables the "One connection per thread" safety check, allowing multiple threads to share the connection
Why it's safe here = We're using SQLAlchemy's connection pooling, so each thread gets its own connection from the pool
default: 
pool_size=5 - Maximum 5 connections in the pool
max_overflow=10 - Can create up to 10 extra temporary connections if needed, so the 16th post/get/put/del will have to wait for one of the connection to be free

so when there is a get, post, put , delete a thread is made to handle that http request. 
and for this thread to talk to the database it uses the connection. connection allows 
communication between the fastapi thread to sqlite. and then the session is what 
quesries the get/post/put/del is asking us to do. 

# HTTP GET /users/1 comes in
# ↓
# FastAPI assigns Thread #5 to handle this request
# ↓  
# Thread #5 calls: db = SessionLocal()
#   - connected to the sdpapp_database.db
#   - Gets Connection #3 from pool
#   - Creates Session using Connection #3
# ↓
# Thread #5 executes: db.query(User).filter(User.id == 1).first()
#   - Session sends SQL through Connection #3 to SQLite file
# ↓
# SQLite returns data → Connection #3 → Session → Thread #5 → HTTP Response
# ↓
# db.close() returns Connection #3 back to pool
"""