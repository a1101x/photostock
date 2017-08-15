from flask import jsonify, request
from flask_classy import route

from .models import Lightbox
from .services import send_get


class LightBoxMixin:

    @route("/add-to-lightbox/", methods=["POST"])
    def add_img_to_lightbox(self):
        lightbox_id = request.form.get('lightbox', '')
        token = request.form.get('token', '')
        lightbox = Lightbox(lightbox_id)

        return jsonify({'status': lightbox.append_item(token)})

    @route("/create-lightbox/", methods=["POST"])
    def create_lightbox(self):
        title = request.form.get('title', '')
        lightbox = Lightbox().create(title)

        return jsonify({'title': lightbox.title,
                        'lightBoxId': lightbox.lightBoxId})

    def get_lightboxes(self):
        resp = []
        status_code, response = send_get('image/lightboxes', nocache=True)
        if status_code == 200:
            resp = response['values']
        return resp
