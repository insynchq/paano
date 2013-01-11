from datetime import datetime
import base64
import os

from werkzeug import secure_filename

from .constants import DEFAULT_LANG, DEFAULT_PLATFORM
from .extensions import db
from .helpers import url_for


def clean_title(s):
    return secure_filename(s)[:64].strip('_').lower().replace('_', '-')


def generate_eid():
    return base64.urlsafe_b64encode(os.urandom(6))


class Question(db.Model):
    category_id = db.Column(db.String(32), primary_key=True)
    eid = db.Column(db.String(8), default=generate_eid, primary_key=True)
    lang = db.Column(db.String(8), default=DEFAULT_LANG, primary_key=True)
    platform = db.Column(db.String(32), default=DEFAULT_PLATFORM,
                         primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    creator = db.Column(db.String(255), nullable=False)

    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, nullable=True)

    position = db.Column(db.Integer, nullable=True)
    is_sticky = db.Column(db.Boolean, default=False)

    @classmethod
    def get_sticky(self, platform):
        return (Question.query
                .filter_by(is_sticky=True)
                .filter(Question.platform.in_([DEFAULT_PLATFORM, platform]))
                .order_by(Question.posted_at.asc())
                .all())

    def url(self, **kwargs):
        kwargs.setdefault('category_id', self.category_id)
        kwargs.setdefault('eid', self.eid)
        kwargs.setdefault('title', clean_title(self.title))
        if kwargs.get('lang') == DEFAULT_LANG:
            kwargs.pop('lang')
        return url_for('question', **kwargs)

    def json(self):
        return dict(
            category_id=self.category_id,
            eid=self.eid,
            lang=self.lang,
            platform=self.platform,
            title=self.title,
            content=self.content,
            creator=self.creator,
            is_sticky=self.is_sticky,
            )


class Category(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    title = db.Column(db.String(32), nullable=False)

    @classmethod
    def create(cls, title):
        category = cls()
        category.id = clean_title(title)
        category.title = title
        return category

    def get_questions(self, platform):
        return (Question.query
                .filter_by(category_id=self.id)
                .filter(Question.platform.in_([DEFAULT_PLATFORM, platform]))
                .order_by(Question.posted_at.asc())
                .all())

    def url(self, **kwargs):
        kwargs.setdefault('category_id', self.id)
        return url_for('category', **kwargs)

    def json(self):
        return dict(id=self.id, title=self.title)
