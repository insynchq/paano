from flask_wtf import (Form, TextField, TextAreaField, SelectField,
                       BooleanField, Required)

from .constants import AVAILABLE_LANGS, AVAILABLE_PLATFORMS


class CategoryForm(Form):
    title = TextField("Title", validators=[Required()])


class QuestionForm(Form):
    category_id = SelectField("Category", validators=[Required()])
    lang = SelectField("Language", choices=AVAILABLE_LANGS,
                       validators=[Required()])
    platform = SelectField("Platform", choices=AVAILABLE_PLATFORMS,
                           validators=[Required()])

    title = TextField("Title", validators=[Required()])
    content = TextAreaField("Content", validators=[Required()])

    is_sticky = BooleanField("Sticky", default=False)
