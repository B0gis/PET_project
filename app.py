from flask import Flask, render_template
from config import Config
import database as db

app = Flask(__name__)
app.config.from_object(Config)

db.db.init_app(app)

from admin import admin_bp
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    latest_news = db.get_published_news(limit=3)
    stats = db.get_stats()
    return render_template('index.html', latest_news=latest_news, stats=stats)

@app.route('/coaches')
def coaches():
    coaches_list = db.get_coaches()
    return render_template('coaches.html', coaches=coaches_list)

@app.route('/schedule')
def schedule():
    schedule_list = db.get_schedule()
    return render_template('schedule.html', schedule=schedule_list)

@app.route('/sportsmen')
def sportsmen():
    sportsmen_list = db.get_sportsmen()
    coaches_list = db.get_coaches()
    return render_template('sportsmen.html', sportsmen=sportsmen_list, coaches=coaches_list)

@app.route('/news')
def news():
    news_list = db.get_published_news()
    return render_template('news.html', news=news_list)

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    news_item = db.get_news_by_id(news_id)
    if not news_item or not news_item.is_published:
        return "Новость не найдена", 404
    return render_template('news_detail.html', news=news_item)

@app.route('/about')
def about():
    return render_template('about.html')

with app.app_context():
    db.db.create_all()
    print("База данных инициализирована!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)