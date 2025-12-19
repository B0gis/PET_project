from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Coach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    sportsmen = db.relationship('Sportsman', backref='coach_rel', lazy=True)
    trainings = db.relationship('Schedule', backref='coach_rel', lazy=True)


class Sportsman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rank = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coach.id'), nullable=False)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coach.id'), nullable=False)
    place = db.Column(db.String(200), nullable=False)


class NewsImage(db.Model):
    """Модель для хранения нескольких изображений новости"""
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)
    thumbnail_path = db.Column(db.String(300))
    is_main = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    order = db.Column(db.Integer, default=0)  # Порядок сортировки

    # Связь с новостью
    news = db.relationship('News', backref=db.backref('images', lazy=True, order_by='NewsImage.order'))


class News(db.Model):
    """Модель новостей (обновленная - без старых полей image_path)"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_published = db.Column(db.Boolean, default=True)

    @property
    def main_image(self):
        """Возвращает главное изображение"""
        for img in self.images:
            if img.is_main:
                return img
        return self.images[0] if self.images else None

    @property
    def thumbnail(self):
        """Возвращает главное изображение для миниатюры (для обратной совместимости)"""
        main_img = self.main_image
        return main_img.thumbnail_path if main_img else None

    @property
    def image_path(self):
        """Свойство для обратной совместимости"""
        main_img = self.main_image
        return main_img.image_path if main_img else None


def check_admin_login(username, password):
    from config import Config
    return username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD


def get_coaches():
    return Coach.query.all()


def get_coach_by_id(coach_id):
    return Coach.query.get(coach_id)


def add_coach(name, experience, phone, email):
    coach = Coach(name=name, experience=experience, phone=phone, email=email)
    db.session.add(coach)
    db.session.commit()


def update_coach(coach_id, name, experience, phone, email):
    coach = Coach.query.get(coach_id)
    if coach:
        coach.name = name
        coach.experience = experience
        coach.phone = phone
        coach.email = email
        db.session.commit()


def delete_coach(coach_id):
    coach = Coach.query.get(coach_id)
    if coach:
        db.session.delete(coach)
        db.session.commit()


def get_sportsmen():
    sportsmen = Sportsman.query.all()
    result = []
    for s in sportsmen:
        coach = Coach.query.get(s.coach_id)
        result.append({
            'id': s.id,
            'name': s.name,
            'rank': s.rank,
            'weight': s.weight,
            'coach_id': s.coach_id,
            'coach_name': coach.name if coach else 'Не назначен'
        })
    return result


def add_sportsman(name, rank, weight, coach_id):
    sportsman = Sportsman(name=name, rank=rank, weight=weight, coach_id=coach_id)
    db.session.add(sportsman)
    db.session.commit()


def update_sportsman(sportsman_id, name, rank, weight, coach_id):
    sportsman = Sportsman.query.get(sportsman_id)
    if sportsman:
        sportsman.name = name
        sportsman.rank = rank
        sportsman.weight = weight
        sportsman.coach_id = coach_id
        db.session.commit()


def delete_sportsman(sportsman_id):
    sportsman = Sportsman.query.get(sportsman_id)
    if sportsman:
        db.session.delete(sportsman)
        db.session.commit()


def get_schedule():
    schedule = Schedule.query.all()
    result = []
    for s in schedule:
        coach = Coach.query.get(s.coach_id)
        result.append({
            'id': s.id,
            'day': s.day,
            'time': s.time,
            'place': s.place,
            'coach_id': s.coach_id,
            'coach_name': coach.name if coach else 'Не назначен'
        })
    return result


def add_training(day, time, coach_id, place):
    training = Schedule(day=day, time=time, coach_id=coach_id, place=place)
    db.session.add(training)
    db.session.commit()


def update_training(training_id, day, time, coach_id, place):
    training = Schedule.query.get(training_id)
    if training:
        training.day = day
        training.time = time
        training.coach_id = coach_id
        training.place = place
        db.session.commit()


def delete_training(training_id):
    training = Schedule.query.get(training_id)
    if training:
        db.session.delete(training)
        db.session.commit()


def get_news():
    return News.query.order_by(News.created_at.desc()).all()


def get_published_news(limit=None):
    query = News.query.filter_by(is_published=True).order_by(News.created_at.desc())
    if limit:
        query = query.limit(limit)
    return query.all()


def get_news_by_id(news_id):
    return News.query.get(news_id)


def add_news_with_images(title, content, images_data=None):
    """Создает новость с несколькими изображениями"""
    news = News(title=title, content=content)
    db.session.add(news)
    db.session.flush()  # Получаем ID новости

    if images_data:
        for i, img_data in enumerate(images_data):
            news_image = NewsImage(
                news_id=news.id,
                image_path=img_data['image_path'],
                thumbnail_path=img_data['thumbnail_path'],
                is_main=(i == 0),  # Первое изображение - главное
                order=i
            )
            db.session.add(news_image)

    db.session.commit()
    return news.id


def update_news_with_images(news_id, title, content, images_data=None, is_published=True):
    """Обновляет новость с изображениями"""
    news = News.query.get(news_id)
    if not news:
        return False

    news.title = title
    news.content = content
    news.is_published = is_published

    if images_data:
        # Добавляем новые изображения
        existing_images_count = NewsImage.query.filter_by(news_id=news_id).count()
        for i, img_data in enumerate(images_data):
            news_image = NewsImage(
                news_id=news_id,
                image_path=img_data['image_path'],
                thumbnail_path=img_data['thumbnail_path'],
                is_main=(existing_images_count + i == 0 and not NewsImage.query.filter_by(news_id=news_id,
                                                                                          is_main=True).first()),
                order=existing_images_count + i
            )
            db.session.add(news_image)

    db.session.commit()
    return True


def delete_news(news_id):
    news = News.query.get(news_id)
    if news:
        # Удаляем все связанные изображения
        NewsImage.query.filter_by(news_id=news_id).delete()
        # Удаляем саму новость
        db.session.delete(news)
        db.session.commit()
        return True
    return False


def toggle_news_publish(news_id):
    news = News.query.get(news_id)
    if news:
        news.is_published = not news.is_published
        db.session.commit()
        return True
    return False


def delete_news_image(image_id):
    """Удаляет одно изображение новости"""
    image = NewsImage.query.get(image_id)
    if image:
        # Если удаляем главное изображение, делаем следующее главным
        if image.is_main:
            next_image = NewsImage.query.filter(
                NewsImage.news_id == image.news_id,
                NewsImage.id != image_id
            ).order_by('order').first()
            if next_image:
                next_image.is_main = True

        db.session.delete(image)
        db.session.commit()

        # Обновляем порядок оставшихся изображений
        remaining_images = NewsImage.query.filter_by(
            news_id=image.news_id
        ).order_by('order').all()

        for i, img in enumerate(remaining_images):
            img.order = i

        db.session.commit()
        return True
    return False


def set_main_news_image(news_id, image_id):
    """Устанавливает изображение как главное"""
    # Сбрасываем все is_main для этой новости
    NewsImage.query.filter_by(news_id=news_id).update({'is_main': False})

    # Устанавливаем выбранное как главное
    image = NewsImage.query.get(image_id)
    if image:
        image.is_main = True
        db.session.commit()
        return True
    return False


def reorder_news_images(news_id, image_order):
    """Изменяет порядок изображений"""
    for image_id, order in image_order.items():
        image = NewsImage.query.get(image_id)
        if image and image.news_id == news_id:
            image.order = order

    db.session.commit()
    return True


def get_stats():
    return {
        'coaches_count': Coach.query.count(),
        'sportsmen_count': Sportsman.query.count(),
        'trainings_count': Schedule.query.count(),
        'news_count': News.query.count(),
        'published_news_count': News.query.filter_by(is_published=True).count(),
        'news_images_count': NewsImage.query.count()
    }



def add_news(title, content, image_path=None, thumbnail_path=None):
    """Старая функция - только для обратной совместимости"""
    return add_news_with_images(title, content, [{
        'image_path': image_path,
        'thumbnail_path': thumbnail_path or image_path
    }] if image_path else None)


def update_news(news_id, title, content, image_path=None, thumbnail_path=None, is_published=True):
    """Старая функция - только для обратной совместимости"""
    return update_news_with_images(news_id, title, content, [{
        'image_path': image_path,
        'thumbnail_path': thumbnail_path or image_path
    }] if image_path else None, is_published)