from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import string
from random import choices

# Init app
app = Flask(__name__)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512))
    short_url = db.Column(db.String(6), unique=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_link()

    def generate_short_link(self):
        characters = string.digits + string.ascii_letters
        short_url = ''.join(choices(characters, k=6))

        link = self.query.filter_by(short_url=short_url).first()

        if link:
            return self.generate_short_link()

        return short_url


@app.route('/shorten_url/', methods=['POST'])
def shorten_url():
    url = request.json['url']
    link = Link.query.filter_by(url=url).first()
    if link:
        return jsonify({"shorten_url": "http://localhost:8000/" + link.short_url, "status": "1"})
    else:
        link = Link(url=url)
        db.session.add(link)
        db.session.commit()
        return jsonify({"shorten_url": "http://localhost:8000/" + link.short_url, "status": "0"})


@app.route('/<short_url>/', methods=['GET'])
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    return jsonify({"url": link.url})

if __name__ == '__main__':
    db.create_all()
    app.run(port=8000, debug=True)
