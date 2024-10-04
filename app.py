import os
import numpy as np
import shutil
from PIL import Image, ImageDraw, ImageFile, UnidentifiedImageError
import matplotlib
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, send_from_directory

ImageFile.LOAD_TRUNCATED_IMAGES = True
matplotlib.use('agg')

app = Flask(__name__)
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdJ8FcqAAAAADEHbAL3F2WTSmBAfA2dMAoG21a1'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdJ8FcqAAAAAFJ3WmDZbWNWblveHUHPNwGKzyno'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # очищаем папку static
        clear_static_files()
        image = request.files['image']
        color = request.form['color']
        cross_type = request.form['cross_type']
        try:
            img = Image.open(image)
            img_with_cross = draw_cross(img, color, cross_type)
            img_with_cross.save('static/cross_image.jpg')
            original_img = Image.open(image)
            plot_color_distribution(original_img, img_with_cross)
        except UnidentifiedImageError:
            return render_template('index.html', error='Выберите файл')

    return render_template('index.html', original_hist='static/color_distribution_orig.jpg', new_hist='static'
                                                                                                      '/color_distribution_transform.jpg')


def clear_static_files():
    shutil.rmtree('static')
    os.makedirs('static')


def draw_cross(img, color, cross_type):
    draw = ImageDraw.Draw(img)
    if cross_type == 'vertical':
        draw = ImageDraw.Draw(img)
        # Рисуем вертикальный крест
        # draw.line((0, 0, 0, img.height), fill=color, width=5)
        # draw.line((0, img.height // 2, img.width, img.height // 2), fill=color, width=5)

        draw.line((img.width // 2, 0, img.width // 2, img.height), fill=color, width=5)  # вертикальная линия
        draw.line((0, img.height // 2, img.width, img.height // 2), fill=color, width=5)  # горизонтальная линия

    elif cross_type == 'horizontal':
        # draw.line((0, 0, img.width, 0), fill=color, width=5)
        # draw.line((img.width // 2, 0, img.width // 2, img.height), fill=color, width=5)
        draw.line((0, 0, img.width, img.height), fill=color, width=5)
        draw.line((0, img.height, img.width, 0), fill=color, width=5)
    return img


def plot_color_distribution(img_orig, img_transform):
    img_array = np.array(img_orig)
    hist, bins = np.histogram(img_array.ravel(), 256, [0, 256])
    plt.bar(bins[:-1], hist)
    plt.xlabel('Color Value')
    plt.ylabel('Frequency')
    plt.title('Color Distribution')
    plt.savefig('static/color_distribution_orig.jpg')
    plt.clf()

    img_array = np.array(img_transform)
    hist, bins = np.histogram(img_array.ravel(), 256, [0, 256])
    plt.bar(bins[:-1], hist)
    plt.xlabel('Color Value')
    plt.ylabel('Frequency')
    plt.title('Color Distribution')
    plt.savefig('static/color_distribution_transform.jpg')
    plt.clf()


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    clear_static_files()
    app.run(debug=True, port=8001)
