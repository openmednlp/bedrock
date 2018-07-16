from sqlalchemy import create_engine

demo_db_string= "postgres://admin:donotusethispassword@aws-us-east-1-portal.19.dblayer.com:15813/compose"

def get_connection(db_string):
    db = create_engine(db_string)
    return db


def create_database(db):
    raise NotImplementedError
    # Creates an empty database based on the MeSH database
    # text file structure
    # db.execute("CREATE TABLE IF NOT EXISTS films (title text, director text, year text)")
    # There is a lot of them
    db.execute('CREATE TABLE IF NOT EXISTS something (col1, col2, col3)')


def populate_database(db):
    raise NotImplementedError
    # Use the MeSH text files to populate the database
    from os import listdir
    from os.path import isfile, join
    file_paths = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file_path in file_paths:
        with open(file_path) as f: # or open as pandas csv
            # db.execute("INSERT INTO films (title, director, year) VALUES ('Doctor Strange', 'Scott Derrickson', '2016')")
            db.execute("INSERT INTO something (col1, col2, col3) VALUES ('', '', '')".format())





