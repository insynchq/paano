from flask_wtf import (Form, TextField, TextAreaField, SelectField,
                       BooleanField, Required)


class CategoryForm(Form):
    title = TextField("Title", validators=[Required()])


class QuestionForm(Form):
    category_id = SelectField("Category", coerce=int, validators=[Required()])
    title = TextField("Title", validators=[Required()])
    content = TextAreaField("Content", validators=[Required()])
    is_sticky = BooleanField("Sticky", default=False)
