from PIL import Image
import os
from werkzeug.utils import secure_filename
import hashlib
import time


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def process_uploaded_image(file, upload_folder='static/uploads/news'):
    if not file or file.filename == '':
        return None, None

    if not allowed_file(file.filename):
        return None, None

    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    timestamp = str(int(time.time()))
    file_content = file.read()
    hash_str = hashlib.md5(file_content).hexdigest()[:8]
    file.seek(0)

    main_filename = f"{name}_{timestamp}_{hash_str}{ext}"
    main_path = os.path.join(upload_folder, main_filename)

    thumb_filename = f"{name}_{timestamp}_{hash_str}_thumb{ext}"
    thumb_path = os.path.join(upload_folder, thumb_filename)

    try:
        img = Image.open(file)

        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        original_width, original_height = img.size
        target_width, target_height = 1920, 1080
        original_ratio = original_width / original_height
        target_ratio = target_width / target_height

        if original_ratio > target_ratio:
            new_width = target_width
            new_height = int(target_width / original_ratio)
        else:
            new_height = target_height
            new_width = int(target_height * original_ratio)

        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        canvas = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        offset_x = (target_width - new_width) // 2
        offset_y = (target_height - new_height) // 2
        canvas.paste(resized_img, (offset_x, offset_y))

        if ext.lower() in ['.jpg', '.jpeg']:
            canvas.save(main_path, 'JPEG', quality=85, optimize=True)
        else:
            canvas.save(main_path, 'PNG', optimize=True)

        thumb_width, thumb_height = 400, 300
        file.seek(0)
        thumb_img = Image.open(file)

        if thumb_img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', thumb_img.size, (255, 255, 255))
            if thumb_img.mode == 'P':
                thumb_img = thumb_img.convert('RGBA')
            background.paste(thumb_img, mask=thumb_img.split()[-1] if thumb_img.mode == 'RGBA' else None)
            thumb_img = background

        thumb_original_width, thumb_original_height = thumb_img.size
        thumb_ratio = thumb_original_width / thumb_original_height

        if thumb_ratio > thumb_width / thumb_height:
            thumb_new_width = thumb_width
            thumb_new_height = int(thumb_width / thumb_ratio)
        else:
            thumb_new_height = thumb_height
            thumb_new_width = int(thumb_height * thumb_ratio)

        thumb_resized = thumb_img.resize((thumb_new_width, thumb_new_height), Image.Resampling.LANCZOS)

        if ext.lower() in ['.jpg', '.jpeg']:
            thumb_resized.save(thumb_path, 'JPEG', quality=75, optimize=True)
        else:
            thumb_resized.save(thumb_path, 'PNG', optimize=True)

        return main_filename, thumb_filename

    except Exception as e:
        print(f"Ошибка при обработке изображения: {str(e)}")
        return None, None