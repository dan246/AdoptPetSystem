import random

class QueryManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def fetch_all_data(self, page_number=1, per_page=10, filter_criteria=None):
        conn = self.db_manager.get_conn()
        cursor = conn.cursor()
        if filter_criteria and filter_criteria != 'all':
            query = "SELECT * FROM animals WHERE animal_kind = ? LIMIT ? OFFSET ?"
            offset = (page_number - 1) * per_page
            cursor.execute(query, (filter_criteria, per_page, offset))
        else:
            query = "SELECT * FROM animals LIMIT ? OFFSET ?"
            offset = (page_number - 1) * per_page
            cursor.execute(query, (per_page, offset))
        return cursor.fetchall()

    def count_all_data(self, filter_criteria=None):
        conn = self.db_manager.get_conn()
        cursor = conn.cursor()
        if filter_criteria and filter_criteria != 'all':
            query = "SELECT COUNT(*) FROM animals WHERE animal_kind = ?"
            cursor.execute(query, (filter_criteria,))
        else:
            query = "SELECT COUNT(*) FROM animals"
            cursor.execute(query)
        return cursor.fetchone()[0]


    def fetch_random_data(self, count=10, filter_criteria=None):
        conn = self.db_manager.get_conn()
        cursor = conn.cursor()
        if filter_criteria and filter_criteria != 'all':
            query = "SELECT * FROM animals WHERE animal_kind = ?"
            cursor.execute(query, (filter_criteria,))
        else:
            query = "SELECT * FROM animals"
            cursor.execute(query)
        all_animals = cursor.fetchall()
        return random.sample(all_animals, min(count, len(all_animals)))