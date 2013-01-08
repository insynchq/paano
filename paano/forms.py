from flask_wtf import (Form, TextField, TextAreaField, QuerySelectField,
                       BooleanField, Required)


class CategoryForm(Form):
    title = TextField("Title", validators=[Required()])


class QuestionForm(Form):
    category_id = QuerySelectField("Category", get_label='title',
                                   validators=[Required()])
    title = TextField("Title", validators=[Required()])
    content = TextAreaField("Content", validators=[Required()])
    is_sticky = BooleanField("Sticky", default=False)
