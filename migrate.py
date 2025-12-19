
from app import app
from database import db, News, NewsImage
import os


def migrate_data():
    with app.app_context():

        db.create_all()

        print("Миграция начата...")


        all_news = News.query.all()
        migrated_count = 0

        for news in all_news:

            try:

                from sqlalchemy import text
                result = db.session.execute(
                    text("SELECT image_path, thumbnail_path FROM news WHERE id = :id"),
                    {"id": news.id}
                ).fetchone()

                if result and result[0]:
                    print(f"Перенос изображения для новости ID {news.id}...")

                    # Создаем запись в NewsImage
                    news_image = NewsImage(
                        news_id=news.id,
                        image_path=result[0],
                        thumbnail_path=result[1] if result[1] else result[0],
                        is_main=True,
                        order=0
                    )
                    db.session.add(news_image)
                    migrated_count += 1

            except Exception as e:
                print(f"Ошибка при миграции новости {news.id}: {e}")
                continue

        db.session.commit()
        print(f"Миграция завершена! Перенесено {migrated_count} изображений.")


if __name__ == '__main__':
    migrate_data()