
from flask import Flask, request, render_template
from database_manager import DatabaseManager
from query_manager import QueryManager
from apscheduler.schedulers.background import BackgroundScheduler
from data_downloader import DataDownloader

app = Flask(__name__)
db_manager = DatabaseManager('animals.db')
data_downloader = DataDownloader("https://data.moa.gov.tw/Service/OpenData/TransService.aspx?UnitId=QcbUEzN6E6DL&IsTransData=1")
query_manager = QueryManager(db_manager)

def update_database():
    print("Updating database with new data...")
    data = data_downloader.fetch_data()
    db_manager.insert_data(data)
    print("Database updated.")

# 設定定時更新資料庫的任務
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_database, trigger="interval", minutes=30)  # 每30分鐘更新一次
scheduler.start()

@app.route('/', methods=['GET'])
def home():
    kind = request.args.get('kind', 'all')  # 從 URL 參數中獲取種類
    page = request.args.get('page', 1, type=int)  # 從 URL 參數中獲取頁碼，預設值為 1
    animals, current_page, total_pages, total_animals = get_animals(kind, page)  # 根據種類和頁碼篩選動物數據
    return render_template('index.html', animals=animals, current_page=current_page, total_pages=total_pages, total_animals=total_animals)

def get_animals(kind, page):
    filter_criteria = None if kind == 'all' else kind
    total_animals = query_manager.count_all_data(filter_criteria=filter_criteria)

    per_page = 10
    total_pages = (total_animals + per_page - 1) // per_page

    # 確保頁碼不會低於1或高於總頁數
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    animals = query_manager.fetch_all_data(page_number=page, per_page=per_page, filter_criteria=filter_criteria)

    return animals, page, total_pages, total_animals





if __name__ == '__main__':
    app.run()