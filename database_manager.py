import sqlite3
from flask import g
from sqlite3 import Error

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file

    def get_conn(self):
        if 'conn' not in g:
            g.conn = sqlite3.connect(self.db_file)
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
