import base64
import os

from flask import (render_template, flash, abort, request, redirect, jsonify,
                   send_from_directory, g, url_for as _url_for)
from flask_googlelogin import UserMixin, login_user, logout_user, current_user
from werkzeug import secure_filename
import misaka as m

from .constants import (DEFAULT_LANG, DEFAULT_PLATFORM, AVAILABLE_PLATFORMS,
                       ALLOWED_EXTS)
from .extensions import login, db
from .forms import CategoryForm, QuestionForm
from .helpers import url_for
from .models import Category, Question
from .wsgi import app


# Setup extensions and hooks


login.init_app(app)
db.init_app(app)


@app.before_request
def detect_platform():
    user_agent = request.headers.get('User-Agent').lower()
    if 'windows' in user_agent:
        g.detected_platform = 'win'
    elif 'macintosh' in user_agent:
        g.detected_platform = 'mac'
    elif 'linux' in user_agent:
        g.detected_platform = 'linux'


@app.teardown_request
def commit_db(exception=None):
    if exception:
        db.session.rollback()
    else:
        db.session.commit()


@app.context_processor
def common():
    params = request.view_args
    available_platforms = []
    for platform, platform_title in AVAILABLE_PLATFORMS:
        if platform == DEFAULT_PLATFORM:
            continue
        params['platform'] = platform
        available_platforms.append((platform, platform_title,
                                    _url_for(request.endpoint, **params)))
    return dict(
        m=m,
        url_for=url_for,
        current_user=current_user,
        selected_lang=request.args.get('lang', DEFAULT_LANG),
        selected_platform=request.args.get('platform', g.detected_platform),
        available_platforms=available_platforms,
        categories=Category.query.order_by(Category.title).all(),
        )


@login.user_loader
def get_user(user_id):
  user = UserMixin()
  user.id = user_id
  user.is_authenticated = lambda: user.id in app.config['ALLOWED_USERS']
  return user


# Routes


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
    selected_platform = request.args.get('platform', g.detected_platform)
    questions = Question.get_sticky(platform=selected_platform)
    return render_template('index.html', questions=questions)


@app.route('/new_category', methods=['GET', 'POST'])
def new_category():
    form = CategoryForm(prefix='category')
    if current_user.is_authenticated() and form.validate_on_submit():
        category = Category.create(form.title.data)
        db.session.add(category)
        db.session.flush()
        flash("Category saved")
        return redirect(category.url())
    return render_template('new_category.html', form=form)


@app.route('/new_question', methods=['GET', 'POST'])
def new_question():
    form_args = dict(prefix='question')

    category_id = request.args.get('category_id')
    eid = request.args.get('eid')
    if category_id and eid:
        base_question = Question.query.filter_by(category_id=category_id,
                                                 eid=eid).first()
        if base_question.platform == DEFAULT_PLATFORM:
            abort(400)
        if not base_question:
            abort(404)
        form_args['obj'] = base_question

    form = QuestionForm(**form_args)

    form.category_id.choices = [(c.id, c.title) for c in
                                Category.query.order_by(Category.title).all()]
    if current_user.is_authenticated() and form.validate_on_submit():
        question = Question()
        question.eid = eid
        question.creator = current_user.id
        form.populate_obj(question)
        db.session.add(question)
        db.session.flush()
        flash("Question saved")
        return redirect(question.url(platform=question.platform))
    else:
        if request.method == 'POST':
            print form.errors

    return render_template('new_question.html', form=form)


@app.route('/categories/<category_id>', methods=['GET', 'POST', 'DELETE'])
def category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'DELETE':
        Question.query.filter_by(category_id=category.id).delete()
        db.session.delete(category)
        return jsonify(success=True)
    selected_platform = request.args.get('platform', g.detected_platform)
    questions = category.get_questions(platform=selected_platform)
    form = CategoryForm(prefix='category', obj=category)
    if current_user.is_authenticated():
        if request.args.get('edit'):
            return render_template('category_form.html', form=form)
        if form.validate_on_submit():
            form.populate_obj(category)
            db.session.add(category)
            db.session.flush()
            flash("Category saved")
            return redirect(category.url())
    return render_template('category.html', category=category,
                           questions=questions)


@app.route('/categories/<category_id>/questions/<eid>/<title>',
           methods=['GET', 'POST', 'DELETE'])
def question(category_id, eid, title):
    category = Category.query.get_or_404(category_id)

    selected_lang = request.args.get('lang', DEFAULT_LANG)
    selected_platform = request.args.get('platform', g.detected_platform)
    question = (Question.query
                .filter_by(category_id=category_id, eid=eid,
                           lang=selected_lang)
                .filter(Question.platform.in_([DEFAULT_PLATFORM,
                                               selected_platform]))
                .first())
    if not question:
        abort(404)

    if request.method == 'DELETE':
        db.session.delete(question)
        return jsonify(success=True)

    form = QuestionForm(prefix='question', obj=question)
    form.category_id.choices = [(c.id, c.title) for c in
                                Category.query.order_by(Category.title).all()]

    if current_user.is_authenticated():
        if request.args.get('edit'):
            return render_template('question_form.html', form=form)
        if form.validate_on_submit():
            form.populate_obj(question)
            db.session.add(question)
            db.session.flush()
            flash("Question saved")
            return redirect(question.url(platform=question.platform))

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
            if any(map(filename.endswith, ALLOWED_EXTS)):
                # Store
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # Return upload path
                return jsonify(filename=url_for('uploads', filename=filename))

    abort(400)


@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
