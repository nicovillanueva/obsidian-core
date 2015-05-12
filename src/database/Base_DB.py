__author__ = 'nico'

import sqlite3, os, logging, sys


class Base_DB(object):
    logger = logging.getLogger("Base_DB")
    dbfile = None

    _creation_statements = {
        "screenshots": '''
                CREATE TABLE IF NOT EXISTS screenshots
                (UID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    url TEXT NOT NULL,
                    browser TEXT NOT NULL,
                    date_taken TEXT NOT NULL,
                    width INT NOT NULL,
                    height INT NOT NULL,
                    filepath TEXT NOT NULL,
                    hash TEXT NOT NULL
                );
                ''',

        "pdiffs": '''
                CREATE TABLE IF NOT EXISTS pdiffs
                (UID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    parents TEXT NOT NULL,
                    width INT,
                    height INT,
                    filepath TEXT,
                    hash TEXT,
                    date TEXT
                );
                '''
    }

    _expected_columns = {
        "screenshots": ["UID", "url", "browser", "date_taken", "width", "height", "filepath", "hash"],
        "pdiffs": ["UID", "parents", "width", "height", "filepath", "hash", "date"]
    }

    def __init__(self, dbfile, safe=False):
        """
        Create or load a SQLite database to use when testing.
        It can also check the integrity of the used DB.
        :param dbfile: Path+filename of the sqlite database to use
        :param safe: Verify the integrity of the database to use
        """
        self.dbfile = dbfile
        if not os.path.isfile(self.dbfile):
            self._create_schema()
            return
        if safe:
            self.logger.info("Checking integrity of database...")
            if not self._check_for_tables():
                self.logger.critical("Tables in the DB do not comply with the schema"
                                     " required in Base_DB.py")
                sys.exit(1)
            self.logger.info("Tables OK")
            if not self._check_for_columns():
                self.logger.critical("Columns in the DB do not comply with the schema"
                                     " required in Base_DB.py")
                sys.exit(1)
            self.logger.info("Columns OK")


    def _create_schema(self):
        conn = sqlite3.connect(self.dbfile)
        conn.execute(self._creation_statements.get("screenshots"))
        conn.execute(self._creation_statements.get("pdiffs"))
        conn.commit()
        conn.close()

    def _check_for_columns(self):
        """
        See which tables are present in the db, and their columns,
        and then compare them to the expected columns defined in
        a dict up above.
        :return: True if the current columns comply to the required ones defined above
        """
        conn = sqlite3.connect(self.dbfile)
        conn.row_factory = lambda cursor, row: row[1]
        tables_in_db = self._get_tables_in_db()
        for table in tables_in_db:
            if ")" in table: return False  # Crappiest SQLi defense ever. TODO: Don't be a dick.
            statement = "PRAGMA table_info(" + table + ");"
            expected = self._expected_columns.get(table)
            table_columns = conn.execute(statement).fetchall()
            for each in expected:
                if each not in table_columns:
                    return False
        return True

    def _check_for_tables(self):
        """
        Gets the expected tables, defined in a dict up above,
        and checks if they are present in the database.
        :return: True if the required tables are in the DB
        """
        columns = self._get_tables_in_db()
        expected_tables = self._creation_statements.keys()
        columns.sort()
        expected_tables.sort()
        return columns == expected_tables

    def _get_tables_in_db(self):
        """
        Retrieve the tables present in the DB
        :return: list of columns
        """
        conn = sqlite3.connect(self.dbfile)
        conn.row_factory = lambda cursor, row: row[0]
        cur = conn.cursor()
        cur.execute('''
            SELECT name FROM sqlite_master
            WHERE type="table"
            AND name NOT LIKE "sqlite?_%" ESCAPE "?";
            '''
        )
        return cur.fetchall()