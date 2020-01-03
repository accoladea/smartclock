from sqlite3 import connect
from smartclock.config.names import database_name
from os import path

"""
    Database Models
    
    Custom function to handle the table doesn't exist in database
"""

# custom method to handle the database if it doesn't exist
appdir = path.abspath(path.dirname(__file__))
database_location = path.join(appdir, database_name)
#
# def database_exists():
#     return path.exists(database_location)

def tableDoesNotExist(tablename):
    con = connect(database_location)
    c = con.cursor()
    c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s' " % tablename)
    if c.fetchone()[0] == 1:
        c.close()
        return False # Table exists
    c.close()
    return True # Table does not exist
