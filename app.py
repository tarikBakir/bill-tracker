#!/usr/bin/env python
from urllib.parse import urlparse, urljoin
import jinja2.exceptions
from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, \
    fresh_login_required, UserMixin, login_manager
from itsdangerous import URLSafeTimedSerializer, SignatureExpired  # after a time the user will logged out automaticlly
from sqlalchemy import insert
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
from forms.login_form import LoginForm
from forms.registration_form import RegistrationForm
from forms.bill_form import BillForm

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
login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = 'You need to login again!'


def is_safe_url(target):  # its safer url when its redirected
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


# @login_manager.user_loader
# def load_User(session_token):  # load_User(user_id):
#   user = User.query.filter_by(session_token=session_token).first()
# user = User.query.get(int(user_id))
# try:
#  serializer.loads(
#       session_token)  # after 100 second the token will be invalid mean its will be automaticlly logged out
# except SignatureExpired:  # if the session is expired then update the session with blink session token
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

    # acc = Account.query.filter_by(
    #   email=email).first()  # passing the USERNAME FROM APP and checking if the user name exists
    # if not acc:
    #  return '<h1>User does not exists</h1>'

    # if check_password_hash(acc.password_hash, request.form.get('password')):
    #   return redirect(url_for('index'))  # if there is nothing in the session

    # else:
    #   flash(u'Incorrect Email or Password!', 'error')
    # return redirect(url_for('login'))

    # return redirect(url_for('register'))

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
    flash('You have been logged Out.')
    return redirect(url_for('profile'))


@app.route('/')
def index():
    # user = User.query.filter_by(username='tarik').first()
    # session_token = serializer.dumps(['tarik', 'admin2'])
    # user.session_token = session_token
    # db.session.commit()
    # login_user(user, remember=True)
    return render_template('index.html')


@app.route('/tables')
def tables():
    return render_template('tables.html')


@app.route('/utilities-other')
def utilities_other():
    return render_template('utilities-other.html')


@app.route('/utilities-color')
def utilities_color():
    return render_template('utilities-color.html')


@app.route('/utilities-animation')
def utilities_animation():
    return render_template('utilities-animation.html')


@app.route('/utilities-border')
def utilities_border():
    return render_template('utilities-border.html')


@app.route('/charts')
def utilities_charts():
    return render_template('charts.html')


@app.route('/cards')
def cards():
    return render_template('cards.html')


@app.route('/buttons')
def buttons():
    return render_template('buttons.html')


@app.route('/blank')
def blank():
    return render_template('blank.html')


@app.route('/add-bill', methods=['GET', 'POST'])
def new_bill():
    companies_list_query = db.select([Company])
    companies_list = db.engine.execute(companies_list_query).fetchall()

    categories_list_query = db.select([Category])
    categories_list = db.engine.execute(categories_list_query).fetchall()

    if request.method == 'POST':
        form = BillForm(request.form)
        if form.paid.data is None:
            form.paid.data = False
        else:
            form.paid.data = True

        if form.validate_on_submit():
            bill = Bill(name=form.name.data, description=form.description.data
                        , amount=form.amount.data, paid=form.paid.data, categoryId=form.categoryId.data,
                        dueDate=form.dueDate.data
                        , companyId=form.companyId.data)
            db.session.add(bill)
            db.session.commit()
            flash('Bill have been saved.')
            return redirect(url_for('bills_list'))

    return render_template('add-bill.html', companies=companies_list, categories=categories_list)


@app.route('/add-company', methods=['GET', 'POST'])
def new_company():
    if request.method == 'POST':
        company = Company(name=request.form["name"], phoneNumber=request.form["phoneNumber"],
                          email=request.form["email"])
        db.session.add(company)
        db.session.commit()
        flash('Company have been saved.')

    return render_template('add-company.html')


@app.route('/add-category', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        category = Category(name=request.form["name"])
        db.session.add(category)
        db.session.commit()
        flash('Category have been saved.')

    return render_template('add-category.html')


@app.route('/bills-list')
def bills_list():
    query = db.select([Bill])
    result = db.engine.execute(query).fetchall()
    return render_template('bills-list.html', bills=result)


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


def get_bills_list(query):
    arr = []
    for record in db.engine.execute(query):
        arr.append(Bill(record.id, record.description, record.name, record.paid, record.amount, record.createDate,
                        record.modifiedDate, record.dueDate, record.companyId, record.categoryId))
    return arr


if __name__ == '__main__':
    db.engine.execute('''DROP TABLE IF EXISTS categories;''')
    db.engine.execute('''DROP TABLE IF EXISTS companies;''')
    db.engine.execute('''DROP TABLE IF EXISTS bills;''')
    db.create_all()
    categories = [
        Category(name="Housing"),
        Category(name="Transportation"),
        Category(name="Food"),
        Category(name="Utilities"),
        Category(name="Clothing"),
        Category(name="Medical/Healthcare"),
        Category(name="Insurance"),
        Category(name="Household Items/Supplies"),
        Category(name="Personal"),
        Category(name="Debt"),
        Category(name="Retirement"),
        Category(name="Education"),
        Category(name="Savings"),
        Category(name="Gifts/Donations"),
        Category(name="Entertainment")
    ]
    db.session.bulk_save_objects(categories)
    db.session.commit()

    companies = [
        Company(name="Netflix", phoneNumber="1800900120", email="contact@netflix.com")
    ]
    db.session.bulk_save_objects(companies)
    db.session.commit()

    bills = [
        Bill(name="Netflix", description="Netflix Subscription", amount=45, paid=False, companyId=1, categoryId=15)
    ]
    db.session.bulk_save_objects(bills)
    db.session.commit()
    app.run(debug=True)
