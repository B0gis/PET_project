from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import database as db
import os
from image_utils import process_uploaded_image

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if db.check_admin_login(username, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin.login'))


def check_auth():
    return session.get('admin_logged_in', False)


@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    if not check_auth():
        return redirect(url_for('admin.login'))
    stats = db.get_stats()
    return render_template('admin/dashboard.html', stats=stats, username=session.get('admin_username'))


# Тренеры
@admin_bp.route('/coaches')
def coaches_list():
    if not check_auth():
        return redirect(url_for('admin.login'))
    coaches = db.get_coaches()
    return render_template('admin/coaches.html', coaches=coaches)


@admin_bp.route('/coaches/add', methods=['GET', 'POST'])
def add_coach():
    if not check_auth():
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        name = request.form.get('name')
        exp = request.form.get('exp')
        phone = request.form.get('phone')
        email = request.form.get('email')
        if name and exp and phone and email:
            db.add_coach(name, exp, phone, email)
            flash('Тренер успешно добавлен', 'success')
            return redirect(url_for('admin.coaches_list'))
        else:
            flash('Заполните все поля', 'danger')
    return render_template('admin/edit_coach.html', coach=None)


@admin_bp.route('/coaches/edit/<int:coach_id>', methods=['GET', 'POST'])
def edit_coach(coach_id):
    if not check_auth():
        return redirect(url_for('admin.login'))
    coach = db.get_coach_by_id(coach_id)
    if not coach:
        flash('Тренер не найден', 'danger')
        return redirect(url_for('admin.coaches_list'))
    if request.method == 'POST':
        name = request.form.get('name')
        exp = request.form.get('exp')
        phone = request.form.get('phone')
        email = request.form.get('email')
        if name and exp and phone and email:
            db.update_coach(coach_id, name, exp, phone, email)
            flash('Тренер успешно обновлен', 'success')
            return redirect(url_for('admin.coaches_list'))
        else:
            flash('Заполните все поля', 'danger')
    return render_template('admin/edit_coach.html', coach=coach)


@admin_bp.route('/coaches/delete/<int:coach_id>')
def delete_coach(coach_id):
    if not check_auth():
        return redirect(url_for('admin.login'))
    db.delete_coach(coach_id)
    flash('Тренер успешно удален', 'success')
    return redirect(url_for('admin.coaches_list'))


# Спортсмены
@admin_bp.route('/sportsmen')
def sportsmen_list():
    if not check_auth():
        return redirect(url_for('admin.login'))
    sportsmen = db.get_sportsmen()
    coaches = db.get_coaches()
    return render_template('admin/sportsmen.html', sportsmen=sportsmen, coaches=coaches)


@admin_bp.route('/sportsmen/add', methods=['GET', 'POST'])
def add_sportsman():
    if not check_auth():
        return redirect(url_for('admin.login'))
    coaches = db.get_coaches()
    if request.method == 'POST':
        name = request.form.get('name')
        rank = request.form.get('rank')
        weight = request.form.get('weight')
        coach_id = request.form.get('coach_id')
        if name and rank and weight and coach_id:
            db.add_sportsman(name, rank, weight, coach_id)
            flash('Спортсмен успешно добавлен', 'success')
            return redirect(url_for('admin.sportsmen_list'))
        else:
            flash('Заполните все поля', 'danger')
    return render_template('admin/edit_sportsman.html', sportsman=None, coaches=coaches)


@admin_bp.route('/sportsmen/edit/<int:sportsman_id>', methods=['GET', 'POST'])
def edit_sportsman(sportsman_id):
    if not check_auth():
        return redirect(url_for('admin.login'))
    sportsmen = db.get_sportsmen()
    coaches = db.get_coaches()
    sportsman = None
    for s in sportsmen:
        if s['id'] == sportsman_id:
            sportsman = s
            break
    if not sportsman:
        flash('Спортсмен не найден', 'danger')
        return redirect(url_for('admin.sportsmen_list'))
    if request.method == 'POST':
        name = request.form.get('name')
        rank = request.form.get('rank')
        weight = request.form.get('weight')
        coach_id = request.form.get('coach_id')
        if name and rank and weight and coach_id:
            db.update_sportsman(sportsman_id, name, rank, weight, coach_id)
            flash('Спортсмен успешно обновлен', 'success')
            return redirect(url_for('admin.sportsmen_list'))
        else:
            flash('Заполните все поля', 'danger')
    return render_template('admin/edit_sportsman.html', sportsman=sportsman, coaches=coaches)


@admin_bp.route('/sportsmen/delete/<int:sportsman_id>')
def delete_sportsman(sportsman_id):
    if not check_auth():
        return redirect(url_for('admin.login'))
    db.delete_sportsman(sportsman_id)
    flash('Спортсмен успешно удален', 'success')
    return redirect(url_for('admin.sportsmen_list'))


# Расписание
@admin_bp.route('/schedule')
def schedule_list():
    if not check_auth():
        return redirect(url_for('admin.login'))
    schedule = db.get_schedule()
    coaches = db.get_coaches()
    return render_template('admin/schedule.html', schedule=schedule, coaches=coaches)


@admin_bp.route('/schedule/add', methods=['GET', 'POST'])
def add_training():
    if not check_auth():
        return redirect(url_for('admin.login'))
    coaches = db.get_coaches()
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    if request.method == 'POST':
        day = request.form.get('day')
        time = request.form.get('time')
        coach_id = request.form.get('coach_id')
        place = request.form.get('place')
        if day and time and coach_id and place:
            db.add_training(day, time, coach_id, place)
            flash('Тренировка успешно добавлена', 'success')
            return redirect(url_for('admin.schedule_list'))
        else:
            flash('Заполните все поля', 'danger')
    return render_template('admin/edit_training.html', training=None, coaches=coaches, days=days)


@admin_bp.route('/schedule/edit/<int:training_id>', methods=['GET', 'POST'])
def edit_training(training_id):
    if not check_auth():
        return redirect(url_for('admin.login'))
    schedule = db.get_schedule()
    coaches = db.get_coaches()
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    training = None
    for t in schedule:
        if t['id'] == training_id:
            training = t
            break
    if not training:
        flash('Тренировка не найдена', 'danger')
        return redirect(url_for('admin.schedule_list'))
    if request.method == 'POST':
        day = request.form.get('day')
        time = request.form.get('time')
        coach_id = request.form.get('coach_id')
        place = request.form.get('place')
        if day and time and coach_id and place:
            db.update_training(training_id, day, time, coach_id, place)
            flash('Тренировка успешно обновлена', 'success')
            return redirect(url_for('admin.schedule_list'))
        else:
            flash('Заполните все поля', 'danger')
    return render_template('admin/edit_training.html', training=training, coaches=coaches, days=days)


@admin_bp.route('/schedule/delete/<int:training_id>')
def delete_training(training_id):
    if not check_auth():
        return redirect(url_for('admin.login'))
    db.delete_training(training_id)
    flash('Тренировка успешно удалена', 'success')
    return redirect(url_for('admin.schedule_list'))



@admin_bp.route('/news')
def news_list():
    if not check_auth():
        return redirect(url_for('admin.login'))
    news_items = db.get_news()
    return render_template('admin/news.html', news=news_items)


@admin_bp.route('/news/add', methods=['GET', 'POST'])
def add_news():
    if not check_auth():
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_published = 'is_published' in request.form


        image_files = request.files.getlist('images')
        images_data = []

        for image_file in image_files:
            if image_file and image_file.filename:
                main_filename, thumb_filename = process_uploaded_image(image_file)
                if main_filename and thumb_filename:
                    images_data.append({
                        'image_path': f"news/{main_filename}",
                        'thumbnail_path': f"news/{thumb_filename}"
                    })

        if title and content:
            news_id = db.add_news_with_images(title, content, images_data)
            if not is_published:
                db.toggle_news_publish(news_id)
            flash('Новость успешно добавлена', 'success')
            return redirect(url_for('admin.news_list'))
        else:
            flash('Заполните заголовок и содержание', 'danger')

    return render_template('admin/edit_news.html', news=None)


@admin_bp.route('/news/edit/<int:news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    if not check_auth():
        return redirect(url_for('admin.login'))

    news_item = db.get_news_by_id(news_id)
    if not news_item:
        flash('Новость не найдена', 'danger')
        return redirect(url_for('admin.news_list'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_published = 'is_published' in request.form


        image_files = request.files.getlist('images')
        images_data = []

        for image_file in image_files:
            if image_file and image_file.filename:
                main_filename, thumb_filename = process_uploaded_image(image_file)
                if main_filename and thumb_filename:
                    images_data.append({
                        'image_path': f"news/{main_filename}",
                        'thumbnail_path': f"news/{thumb_filename}"
                    })

        if title and content:

            delete_images = request.form.getlist('delete_images')
            for image_id in delete_images:
                db.delete_news_image(int(image_id))


            main_image_id = request.form.get('main_image')
            if main_image_id:
                db.set_main_news_image(news_id, int(main_image_id))


            order_data = {}
            for key, value in request.form.items():
                if key.startswith('order_'):
                    image_id = int(key.replace('order_', ''))
                    order_data[image_id] = int(value)

            if order_data:
                db.reorder_news_images(news_id, order_data)


            db.update_news_with_images(news_id, title, content, images_data, is_published)
            flash('Новость успешно обновлена', 'success')
            return redirect(url_for('admin.news_list'))
        else:
            flash('Заполните заголовок и содержание', 'danger')

    return render_template('admin/edit_news.html', news=news_item)


@admin_bp.route('/news/delete/<int:news_id>')
def delete_news(news_id):
    if not check_auth():
        return redirect(url_for('admin.login'))
    news_item = db.get_news_by_id(news_id)
    if news_item and news_item.images:
        # Удаляем файлы изображений
        for image in news_item.images:
            img_path = os.path.join('static/uploads', image.image_path)
            thumb_path = os.path.join('static/uploads', image.thumbnail_path)
            if os.path.exists(img_path):
                os.remove(img_path)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
    db.delete_news(news_id)
    flash('Новость успешно удалена', 'success')
    return redirect(url_for('admin.news_list'))


@admin_bp.route('/news/toggle/<int:news_id>')
def toggle_news(news_id):
    if not check_auth():
        return redirect(url_for('admin.login'))
    if db.toggle_news_publish(news_id):
        flash('Статус публикации изменен', 'success')
    else:
        flash('Ошибка при изменении статуса', 'danger')
    return redirect(url_for('admin.news_list'))


@admin_bp.route('/news/image/delete/<int:image_id>')
def delete_news_image(image_id):
    """Удаляет одно изображение новости"""
    if not check_auth():
        return redirect(url_for('admin.login'))

    if db.delete_news_image(image_id):
        flash('Изображение удалено', 'success')
    else:
        flash('Ошибка при удалении изображения', 'danger')

    return redirect(request.referrer or url_for('admin.news_list'))


@admin_bp.route('/news/image/set_main/<int:news_id>/<int:image_id>')
def set_main_news_image(news_id, image_id):
    """Устанавливает изображение как главное"""
    if not check_auth():
        return redirect(url_for('admin.login'))

    if db.set_main_news_image(news_id, image_id):
        flash('Главное изображение изменено', 'success')
    else:
        flash('Ошибка при изменении главного изображения', 'danger')

    return redirect(request.referrer or url_for('admin.news_list'))