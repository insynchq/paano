import base64
import os

from flask import (Flask, render_template, flash, abort, request, redirect,
                   jsonify)
from werkzeug import secure_filename
import misaka as m

from .extensions import db
from .forms import CategoryForm, QuestionForm
from .models import Category, Question

ALLOWED_EXT = set(['.png', '.jpg', '.jpeg', '.gif'])
UPLOADS_FOLDER = 'uploads'


app = Flask(__name__)
app.config.from_object('paano.config')

db.init_app(app)


@app.teardown_request
def teardown_request(exception=None):
  if not exception:
    db.session.commit()


@app.context_processor
def sidebar():
    return dict(m=m, categories=Category.query.all())


@app.route('/')
def index():
    questions = Question.query.filter_by(is_sticky=True).all()
    return render_template('index.html', questions=questions)


@app.route('/new_category', methods=['GET', 'POST'])
def new_category():
    form = CategoryForm(prefix='category')
    if form.validate_on_submit():
        category = Category()
        form.populate_obj(category)
        db.session.add(category)
        db.session.flush()
        flash("Category saved")
        return redirect(category.url())
    return render_template('new_category.html', form=form)


@app.route('/new_question', methods=['GET', 'POST'])
def new_question():
    form = QuestionForm(prefix='question')
    form.category_id.choices = [(c.id, c.title) for c in
                                Category.query.order_by(Category.title).all()]
    if form.validate_on_submit():
        question = Question()
        form.populate_obj(question)
        db.session.add(question)
        db.session.flush()
        flash("Question saved")
        return redirect(question.url())
    return render_template('new_question.html', form=form)


@app.route('/<category_title>/<category_id>', methods=['GET', 'POST'])
def category(category_title, category_id):
    category = Category.query.get_or_404(category_id)
    questions = Question.query.filter_by(category_id=category_id).all()
    form = CategoryForm(prefix='category', obj=category)
    if request.args.get('edit'):
        return render_template('edit_category.html', form=form)
    if form.validate_on_submit():
        form.populate_obj(category)
        db.session.add(category)
        db.session.flush()
        return redirect(category.url())
        flash("Category saved")
    return render_template('category.html', category=category,
                           questions=questions)


@app.route('/<category_title>/<category_id>/<question_title>/<question_id>',
           methods=['GET', 'POST'])
def question(category_title, category_id, question_title, question_id):
    category = Category.query.get_or_404(category_id)
    question = Question.query.filter_by(category_id=category_id,
                                        id=question_id).first()
    if not question:
        abort(404)
    form = QuestionForm(prefix='question', obj=question)
    form.category_id.choices = [(c.id, c.title) for c in
                                Category.query.order_by(Category.title).all()]
    if request.args.get('edit'):
        return render_template('edit_question.html', form=form)
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.add(question)
        db.session.flush()
        return redirect(question.url())
        flash("Question saved")
    return render_template('question.html', category=category,
                           question=question)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('userfile')
        if f:
            # Add a random prefix to keep filenames unique
            filename = (base64.urlsafe_b64encode(os.urandom(9)) + '_' +
                        secure_filename(f.filename))
            # Check if has valid extension
            if any(map(filename.endswith, ALLOWED_EXT)):
                # Store
                f.save(os.path.join(app.static_folder, UPLOADS_FOLDER,
                                    filename))
                # Return upload path
                return jsonify(filename=os.path.join(app.static_url_path,
                                                     UPLOADS_FOLDER, filename))

    abort(400)
