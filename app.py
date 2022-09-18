#!/usr/bin/env python
from urllib.parse import urlparse, urljoin
import jinja2.exceptions
from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, \
    fresh_login_required, UserMixin, login_manager
from itsdangerous import URLSafeTimedSerializer, SignatureExpired  # after a time the user will logged out automaticlly
from werkzeug.security import check_password_hash

from database import db
from models.account import Account
from models.account_preferences import Account_Preference
from models.address import Address
from models.company import Company
from models.user import User
from models.notification import Notification
from models.category import Category
from models.bill import Bill
from registration import RegistrationForm
from login import LoginForm


login_manager = LoginManager()




def create_app():
    global app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['USER_ENABLE_EMAIL'] = True
    app.config['USER_ENABLE_FORGOT_PASSWORD'] = True
    app.config['SECRET_KEY'] = 'secret'
    db.app = app
    #
    login_manager.init_app(app)

    db.init_app(app)

    @login_manager.user_loader
    def load_user(email):
        return Account.query.get(email)


    return app


app = create_app()


serializer = URLSafeTimedSerializer(app.secret_key)
login_manager.login_view = 'login'
login_manager.login_message = 'the email or password are incorrect.'
#login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = 'You need to login again!'


def is_safe_url(target):  # its safer url when its redirected
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


#@login_manager.user_loader
#def load_User(session_token):  # load_User(user_id):
 #   user = User.query.filter_by(session_token=session_token).first()
    # user = User.query.get(int(user_id))
    #try:
      #  serializer.loads(
     #       session_token)  # after 100 second the token will be invalid mean its will be automaticlly logged out
    #except SignatureExpired:  # if the session is expired then update the session with blink session token
      #  user.session_token = None
     #   db.session.commit()
    #    return None  # if the session is invalid or doesn't find the user
   # return user


@app.route('/profile')
@login_required
def profile():
    return f'<h1>You are in the profile, {current_user.userName}.</h1>'  ## printing the current user that logging in


@app.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        account = Account.query.filter_by(email=form.email.data).first()
        if account is not None and account.verify_password(form.password.data):
            login_user(account, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid email or password.')
    return render_template('login.html', form=form)

        # remember_me = request.form.get('remember_me')

        #acc = Account.query.filter_by(
         #   email=email).first()  # passing the USERNAME FROM APP and checking if the user name exists
        #if not acc:
          #  return '<h1>User does not exists</h1>'

        #if check_password_hash(acc.password_hash, request.form.get('password')):
         #   return redirect(url_for('index'))  # if there is nothing in the session

        #else:
         #   flash(u'Incorrect Email or Password!', 'error')
        #return redirect(url_for('login'))


        #return redirect(url_for('register'))

    #     login_user(user)  # remember me token is true when there is a vin checkbox else False
    #     if 'next' in session and session['next']:
    #         if is_safe_url(session['next']):
    #             return redirect(session['next'])
    #
    #     return '<h1>you are now logged in.</h>'
    #
    # session['next'] = request.args.get('next')



@app.route('/logout')
@login_required  # u can only log out if u logging in
def logout():
    logout_user()
    return '<h1>you are now logged out.</h1>'


@app.route('/')
def index():
    # user = User.query.filter_by(username='tarik').first()
    # session_token = serializer.dumps(['tarik', 'admin2'])
    # user.session_token = session_token
    # db.session.commit()
    # login_user(user, remember=True)
    return render_template('index.html')


@app.route('/change')
@fresh_login_required
def change():
    return '<h1>This is for fresh logins only!</h1>'


# to run unit tests (venv) $ flask test
# class UserModelTestCase(unittest.TestCase):
#     def test_password_setter(self):
#         u = User(password='cat')
#         self.assertTrue(u.password_hash is not None)
#
#     def test_no_password_getter(self):
#         u = User(password='cat')
#         with self.assertRaises(AttributeError):
#             u.password
#
#     def test_password_verification(self):
#         u = User(password='cat')
#         self.assertTrue(u.verify_password('cat'))
#         self.assertFalse(u.verify_password('dog'))
#
#     def test_password_salts_are_random(self):
#         u = User(password='cat')
#         u2 = User(password='cat')
#         self.assertTrue(u.password_hash != u2.password_hash)


# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = RegistrationForm(request.form)
        if form.validate_on_submit():
            account = Account(email=form.email.data,
                              password=form.password.data)
            db.session.add(account)
            user = User(firstname=form.firstName.data, lastname=form.lastName.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash('You can now login.')
            return redirect(url_for('login'))
    return render_template('register.html')


# def create_user(self):
#     user = User(username='tarik', password='admin1', session_token=serializer.dumps(
#         ['username', 'password']))  # not sure if this is the correct way to pass the parameters
#     db.session.add(user)
#     db.session.commit()
#
# def update_token(self):
#     tarik = User.query.filter_by(username='tarik').first()
#     tarik.password = 'admin2'
#     tarik.session_token = serializer.dumps(['tarik', 'admin2'])
#     db.session.commit()

# @app.route('/<pagename>')
# def admin(pagename):
#     return render_template(pagename + '.html')


@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
