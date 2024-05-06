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
