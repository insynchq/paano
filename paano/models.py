from datetime import datetime

from flask import url_for
from werkzeug import secure_filename

from .extensions import db


def clean(s):
    return secure_filename(s).lower()[:16]


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime)
    is_sticky = db.Column(db.Boolean, default=False)

    def url(self, category=None, **kwargs):
        if not category:
            category = Category.query.get(self.category_id)
        return url_for('question', category_title=clean(category.title),
                       category_id=category.id,
                       question_title=clean(self.title), question_id=self.id,
                       **kwargs)

    def json(self):
        return dict(id=self.id,
                    category_id=self.category_id,
                    title=self.title,
                    content=self.content,
                    is_sticky=self.is_sticky)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)

    def get_questions(self):
        return (Question.query.filter_by(category_id=self.id)
                .order_by(Question.posted_at.asc()).all())

    def url(self, **kwargs):
        return url_for('category', category_title=clean(self.title),
                       category_id=self.id, **kwargs)

    def json(self):
        return dict(id=self.id, title=self.title)
