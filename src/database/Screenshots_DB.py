__author__ = 'Nico'

from Base_DB import Base_DB
import sqlite3


class Screenshots_DB(Base_DB):
    """
    Class that manages the database (sqlite) that holds references to the taken screenshots
    It can create the schema, insert new screenshot references, delete them, and search for them.
    """

    def store_screenshots(self, screenshots):
        conn = sqlite3.connect(self.dbfile)
        for screen in screenshots:
            conn.execute(
                "INSERT INTO screenshots (url, browser, date_taken, width, height, filepath, hash)\
                VALUES (?,?,?,?,?,?,?);",
                (screen.url, screen.browser, screen.date_taken, screen.width,
                 screen.height, screen.path, screen.hashvalue)
            )
        conn.commit()
        conn.close()

    def get_by_date(self, day=None, month=None, year=None):
        raise NotImplementedError

    def get_by_browser(self, browser="firefox", amount=1):
        conn = sqlite3.connect(self.dbfile)
        conn.row_factory = lambda cursor, row: row[0]
        cur = conn.cursor()
        cur.execute(
            "SELECT filepath FROM screenshots WHERE browser = ?;",
            (browser,)
        )
        return cur.fetchmany(amount)

    def get_by_url(self, url=None):
        raise NotImplementedError

    def get_by_id(self, uid, *extraids):
        conn = sqlite3.connect(self.dbfile)
        conn.row_factory = lambda cursor, row: row[0]
        cur = conn.cursor()

        allids = [int(uid)]
        if extraids is not None:
            allids.extend(list(extraids))

        cur.execute(
            "SELECT filepath FROM screenshots WHERE UID IN (%s);" % ",".join("?" * len(allids)),
            tuple(allids)
        )
        results = cur.fetchall()
        return results[0] if len(results) < 2 else results
