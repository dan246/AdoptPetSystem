from flask import Flask, request, render_template, redirect, url_for, session
from database_manager import DatabaseManager
from query_manager import QueryManager
from apscheduler.schedulers.background import BackgroundScheduler
from data_downloader import DataDownloader
import random
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'
db_manager = DatabaseManager('animals.db')
data_downloader = DataDownloader("https://data.moa.gov.tw/Service/OpenData/TransService.aspx?UnitId=QcbUEzN6E6DL&IsTransData=1")
query_manager = QueryManager(db_manager)

with app.app_context():
    db_manager.create_table()

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
    display_pages = get_display_pages(current_page, total_pages)  # 獲取顯示的頁碼範圍
    return render_template('index.html', animals=animals, current_page=current_page, total_pages=total_pages, display_pages=display_pages, kind=kind, total_animals=total_animals)

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

def get_display_pages(current_page, total_pages, window=2):
    """Generate a range of page numbers around the current page."""
    start = max(current_page - window, 1)
    end = min(current_page + window, total_pages) + 1
    return range(start, end)

@app.route('/draw', methods=['GET'])
def draw():
    draw_kind = request.args.get('draw_kind', 'all')
    animals = draw_animals(draw_kind, count=10)  # 隨機抽取10隻動物
    return render_template('draw.html', animals=animals)

def draw_animals(kind, count=10):
    filter_criteria = None if kind == 'all' else kind
    all_animals = query_manager.fetch_random_data(filter_criteria=filter_criteria)
    return random.sample(all_animals, min(count, len(all_animals)))  # 避免抽取數量超過總數

# 使用者註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        db_manager.insert_user(username, hashed_password, email)
        return redirect(url_for('login'))
    return render_template('register.html')

# 使用者登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = db_manager.verify_user(username, hashed_password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

# 使用者登出
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

# 發表新帖
@app.route('/post', methods=['GET', 'POST'])
def post():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']
        
        db_manager.insert_post(title, content, user_id)
        return redirect(url_for('forum'))
    return render_template('post.html')

# 討論區
@app.route('/forum')
def forum():
    posts = db_manager.fetch_all_posts()
    return render_template('forum.html', posts=posts)

# 單個帖子及評論
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        content = request.form['content']
        user_id = session['user_id']
        
        db_manager.insert_comment(post_id, content, user_id)
    
    post = db_manager.fetch_post_by_id(post_id)
    comments = db_manager.fetch_comments_by_post_id(post_id)
    return render_template('post_detail.html', post=post, comments=comments)

if __name__ == '__main__':
    app.run()
