import sqlite3
from flask import g
from sqlite3 import Error

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file

    def get_conn(self):
        if 'conn' not in g:
            g.conn = sqlite3.connect(self.db_file)
            g.conn.row_factory = sqlite3.Row  # 使查詢返回字典
        return g.conn

    def close_conn(self):
        conn = g.pop('conn', None)
        if conn is not None:
            conn.close()

    def create_table(self):
        try:
            c = self.get_conn()
            c.execute('''
                CREATE TABLE IF NOT EXISTS animals (
                    animal_id INTEGER PRIMARY KEY,
                    animal_subid TEXT,
                    animal_area_pkid INTEGER,
                    animal_shelter_pkid INTEGER,
                    animal_place TEXT,
                    animal_kind TEXT,
                    animal_variety TEXT,
                    animal_sex TEXT,
                    animal_bodytype TEXT,
                    animal_colour TEXT,
                    animal_age TEXT,
                    animal_sterilization TEXT,
                    animal_bacterin TEXT,
                    animal_foundplace TEXT,
                    animal_title TEXT,
                    animal_status TEXT,
                    animal_remark TEXT,
                    animal_opendate TEXT,
                    animal_closeddate TEXT,
                    animal_update TEXT,
                    animal_createtime TEXT,
                    shelter_name TEXT,
                    album_file TEXT,
                    shelter_address TEXT,
                    shelter_tel TEXT
                );
            ''')
            c.commit()
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL
                );
            ''')
            c.commit()
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
            ''')
            c.commit()
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
            ''')
            c.commit()
            
        except Error as e:
            print(e)

    def insert_data(self, data):
        try:
            conn = self.get_conn()
            if conn is not None:
                c = conn.cursor()
                # 檢查 data 是否為列表形式，如果不是則封裝成列表
                if isinstance(data, dict):
                    data = [data]

                # 轉換 dict 至 tuple
                prepared_data = [
                    (
                        d["animal_id"], d["animal_subid"], d["animal_area_pkid"], d["animal_shelter_pkid"], 
                        d["animal_place"], d["animal_kind"], d.get("animal_variety", "").strip(), d["animal_sex"], 
                        d["animal_bodytype"], d["animal_colour"], d["animal_age"], d["animal_sterilization"], 
                        d["animal_bacterin"], d["animal_foundplace"], d["animal_title"], d["animal_status"], 
                        d["animal_remark"], d["animal_opendate"], d["animal_closeddate"], d["animal_update"], 
                        d["animal_createtime"], d["shelter_name"], d["album_file"], d["shelter_address"], 
                        d["shelter_tel"]
                    ) for d in data
                ]
                c.executemany('''
                    INSERT OR REPLACE INTO animals (animal_id, animal_subid, animal_area_pkid, animal_shelter_pkid, animal_place, 
                        animal_kind, animal_variety, animal_sex, animal_bodytype, animal_colour, animal_age, 
                        animal_sterilization, animal_bacterin, animal_foundplace, animal_title, animal_status, 
                        animal_remark, animal_opendate, animal_closeddate, animal_update, animal_createtime, 
                        shelter_name, album_file, shelter_address, shelter_tel)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                ''', prepared_data)
                conn.commit()
                c.close()
        except sqlite3.Error as e:
            print(f"Error inserting data into database: {e}")

    def insert_user(self, username, password, email):
        try:
            conn = self.get_conn()
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (username, password, email) 
                VALUES (?, ?, ?)
            ''', (username, password, email))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting user into database: {e}")

    def verify_user(self, username, password):
        try:
            conn = self.get_conn()
            c = conn.cursor()
            c.execute('''
                SELECT * FROM users 
                WHERE username = ? AND password = ?
            ''', (username, password))
            return c.fetchone()
        except sqlite3.Error as e:
            print(f"Error verifying user: {e}")
            return None

    def insert_post(self, title, content, user_id):
        try:
            conn = self.get_conn()
            c = conn.cursor()
            c.execute('''
                INSERT INTO posts (title, content, user_id) 
                VALUES (?, ?, ?)
            ''', (title, content, user_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting post into database: {e}")

    def fetch_all_posts(self):
        try:
            conn = self.get_conn()
            c = conn.cursor()
            c.execute('''
                SELECT posts.*, users.username 
                FROM posts 
                JOIN users ON posts.user_id = users.id 
                ORDER BY created_at DESC
            ''')
            return c.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching posts: {e}")
            return []

    def fetch_post_by_id(self, post_id):
        try:
            conn = self.get_conn()
            c = conn.cursor()
            c.execute('''
                SELECT posts.*, users.username 
                FROM posts 
                JOIN users ON posts.user_id = users.id 
                WHERE posts.id = ?
            ''', (post_id,))
            return c.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching post by id: {e}")
            return None

    def insert_comment(self, post_id, content, user_id):
        try:
            conn = self.get_conn()
            c = conn.cursor()
            c.execute('''
                INSERT INTO comments (post_id, content, user_id) 
                VALUES (?, ?, ?)
            ''', (post_id, content, user_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting comment into database: {e}")

    def fetch_comments_by_post_id(self, post_id):
        try:
            conn = self.get_conn()
            c = conn.cursor()
            c.execute('''
                SELECT comments.*, users.username 
                FROM comments 
                JOIN users ON comments.user_id = users.id 
                WHERE post_id = ? 
                ORDER BY created_at ASC
            ''', (post_id,))
            return c.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching comments by post id: {e}")
            return []

