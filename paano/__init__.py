import base64
import os

from flask import (Flask, render_template, flash, abort, request, redirect,
                   jsonify, url_for)
from flask_googlelogin import UserMixin, login_user, logout_user, current_user
from werkzeug import secure_filename
import misaka as m

from .extensions import login, db
from .forms import CategoryForm, QuestionForm
from .models import Category, Question

ALLOWED_EXT = set(['.png', '.jpg', '.jpeg', '.gif'])
UPLOADS_FOLDER = 'uploads'


app = Flask(__name__)
app.config.from_object('paano.config')

login.init_app(app)
db.init_app(app)


@app.teardown_request
def teardown_request(exception=None):
  if not exception:
    db.session.commit()


@app.context_processor
def common():
    return dict(m=m, current_user=current_user,
                categories=Category.query.order_by(Category.title).all())


@login.user_loader
def get_user(user_id):
  user = UserMixin()
  user.id = user_id
  user.is_authenticated = lambda: user.id in app.config['ALLOWED_USERS']
  return user


@app.route('/login')
def login_redirect():
    return redirect(login.login_manager.login_view)


@app.route('/oauth2callback')
@login.oauth2callback
def oauth2callback(userinfo):
    user = login.login_manager.user_callback(userinfo['id'])
    login_user(user)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
def index():
    questions = (Question.query.filter_by(is_sticky=True)
                 .order_by(Question.posted_at.asc()).all())
    return render_template('index.html', questions=questions)


@app.route('/new_category', methods=['GET', 'POST'])
def new_category():
    form = CategoryForm(prefix='category')
    if current_user.is_authenticated() and form.validate_on_submit():
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
    if current_user.is_authenticated() and form.validate_on_submit():
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
    questions = category.get_questions()
    form = CategoryForm(prefix='category', obj=category)
    if current_user.is_authenticated():
        if request.args.get('edit'):
            return render_template('edit_category.html', form=form)
        if form.validate_on_submit():
            form.populate_obj(category)
            db.session.add(category)
            db.session.flush()
            flash("Category saved")
            return redirect(category.url())
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
    if current_user.is_authenticated():
        if request.args.get('edit'):
            return render_template('edit_question.html', form=form)
        if form.validate_on_submit():
            form.populate_obj(question)
            db.session.add(question)
            db.session.flush()
            flash("Question saved")
            return redirect(question.url())
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
