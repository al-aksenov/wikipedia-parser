import sqlite3

conn = sqlite3.connect("urls.db")
cursor = conn.cursor()
sql = """
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY,
            url TEXT,
            request_depth INTEGER
            );
      """
cursor.execute(sql)
sql = """
        CREATE TABLE IF NOT EXISTS refs (
            from_page_id INTEGER,
            link_id INTEGER,
            FOREIGN KEY(from_page_id, link_id) REFERENCES pages(id, id)
            );
      """
cursor.execute(sql)
conn.commit()
conn.close()
