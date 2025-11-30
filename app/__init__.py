# app/__init__.py

from app.database import close_mongo_connection, connect_to_mongo, db, get_database

__all__ = ["db", "connect_to_mongo", "close_mongo_connection", "get_database"]
