#!/usr/bin/env python
from urllib.parse import urlparse, urljoin
import jinja2.exceptions
from flask import Flask, render_template, session, request, redirect, url_for, flash, make_response, abort, Blueprint
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, \
    fresh_login_required, UserMixin, login_manager
from itsdangerous import URLSafeTimedSerializer, SignatureExpired  # after a time the user will logged out automaticlly
from sqlalchemy import insert, and_
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from database import db
from forms.changePassword_form import changePasswordFrom
from models.account import Account
from models.account_preferences import Account_Preference
from models.address import Address
from models.notification import Notification
from forms.EditProfile_form import editProfileForm
from models.company import Company
from models.user import User
from models.category import Category
from models.bill import Bill
from forms.login_form import LoginForm
from forms.registration_form import RegistrationForm
from forms.bill_form import BillForm
from flask_mail import Mail, Message
from threading import Thread
import re
import os

from flask_change_password import ChangePassword, ChangePasswordForm, SetPasswordForm
from flask_moment import Moment

# basedir = os.path.abspath(os.path.dirname(__file__))

login_manager = LoginManager()


def create_app():
    global app
    app = Flask(__name__)
    # app.config.from_object('config')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['USER_ENABLE_EMAIL'] = True
    app.config['USER_ENABLE_FORGOT_PASSWORD'] = True
    app.config['SECRET_KEY'] = 'secret'

    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

    # app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
    # app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <bluguuy32@gmail.com>'
    # app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
    db.app = app
    app.app_context().push()

    login_manager.init_app(app)

    db.init_app(app)

    return app


@login_manager.user_loader
def load_user(email):
    return Account.query.get(email)


app = create_app()
mail = Mail(app)

serializer = URLSafeTimedSerializer(app.secret_key)
login_manager.login_view = 'login'
login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = 'You need to login again!'


def is_safe_url(target):  # its safer url when its redirected
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            account = Account.query.filter_by(email=form.email.data).first()
            if account is not None and account.verify_password(form.password.data):
                login_user(account, form.remember_me.data)
                next = request.args.get('next')
                if not is_safe_url(next):
                    return abort(400)
                resp = make_response(render_template('login.html', form=form, email=form.email.data))
                resp.set_cookie('user_email', form.email.data)
                return redirect(request.args.get('next') or url_for('index'))
            else:
                flash("incorrect password or email!")

    return render_template('login.html', form=form, email=form.email.data)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged Out.')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    totalUnpaidBills = db.engine.execute(
        'Select count(b.id) AS totalunpaidbills from bills as b inner join users as u on b.userId = u.id where b.paid = 0 and u.email=? GROUP BY b.userId',
        current_user.email).first()
    if totalUnpaidBills is None:
        totalUnpaidBills = 0
    else:
        totalUnpaidBills = totalUnpaidBills.totalunpaidbills

    totalBill = db.engine.execute(
        'Select COUNT(b.id) AS totalBill from bills as b inner join users as u on b.userId = u.id where u.email=?  GROUP BY b.userId',
        current_user.email).first()
    if totalBill is None:
        totalBill = 0
    else:
        totalBill = totalBill.totalBill

    monthlyBillsAmount = db.engine.execute(
        'SELECT SUM(amount) AS total FROM bills as b inner join users u on b.userId = u.id WHERE u.email=? and dueDate > DATETIME("now", "-31 day") AND b.paid = 0',
        current_user.email).first()
    if monthlyBillsAmount is None:
        monthlyBillsAmount = 0
    else:
        monthlyBillsAmount = monthlyBillsAmount.total

    paidMonthlyBillsAmount = db.engine.execute(
        'SELECT SUM(amount) AS total FROM bills inner join users as u on bills.userId=u.id WHERE dueDate > DATETIME("now", "-31 day") AND paid = 1 AND u.email=?',
        current_user.email).first()

    if paidMonthlyBillsAmount is None:
        paidMonthlyBillsAmount = 0
    else:
        paidMonthlyBillsAmount = paidMonthlyBillsAmount.total

    billsAmountByMonth = db.engine.execute(
        "SELECT b.userId,strftime('%m', b.dueDate) AS 'Month',sum(b.amount) AS 'monthlyPayment' ,count(b.id) AS 'number Of Bills' from bills AS b inner join users as u on b.userId = u.id where b.paid=0 and  (date('now')-date(b.dueDate))<=1 AND u.email=? group by b.userId,Month ORDER BY Month ASC",
        current_user.email).fetchall()

    billsAmountByMonth_amountsMapped = list(map(lambda b: b.monthlyPayment, billsAmountByMonth))

    topFiveCategories = db.engine.execute(
        'select c.name as category, count(b.id) as NumberOfBills from categories as c inner join bills as b on c.id = b.categoryId inner join users u on b.userId = u.id where u.email=? group by c.name order by NumberOfBills DESC limit 5',
        current_user.email).fetchall()

    topFiveCategories_names = list(map(lambda b: b.category, topFiveCategories))
    topFiveCategories_amount = list(map(lambda b: b.NumberOfBills, topFiveCategories))

    user = db.engine.execute('Select * from users where email=?', current_user.email).fetchall()[0]
    return render_template('index.html',
                           user_name=user.firstname + ' ' + user.lastname,
                           totalUnpaid=str(monthlyBillsAmount), totalPaid=str(paidMonthlyBillsAmount),
                           billsAmountByMonth=billsAmountByMonth_amountsMapped,
                           topFiveCategories_names=topFiveCategories_names,
                           topFiveCategories_amount=topFiveCategories_amount,
                           totalBills=str(totalBill),
                           totalUnpaidBills=str(totalUnpaidBills))


@app.route('/blank')
@login_required
def blank():
    return render_template('blank.html')


@app.route('/forgot-password')
def forgot_password():
    return render_template('change-password.html')


@app.route('/add-bill', methods=['GET', 'POST'])
@login_required
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
            user_id = db.engine.execute('Select * from users where email=?', current_user.email).fetchall()[0].id

            bill = Bill(name=form.name.data, description=form.description.data
                        , amount=form.amount.data, paid=form.paid.data, categoryId=form.categoryId.data,
                        dueDate=form.dueDate.data, companyId=form.companyId.data, userId=user_id)
            db.session.add(bill)
            db.session.commit()
            flash('Bill have been saved.')
            return redirect(url_for('bills_list'))

    return render_template('add-bill.html', companies=companies_list, categories=categories_list)


@app.route('/edit-bill/<bill_id>', methods=['GET', 'POST'])
@login_required
def edit_bill(bill_id):
    user_id = db.engine.execute('Select * from users where email=?', current_user.email).fetchall()[0].id
    companies_list_query = db.select([Company])
    companies_list = db.engine.execute(companies_list_query).fetchall()

    categories_list_query = db.select([Category])
    categories_list = db.engine.execute(categories_list_query).fetchall()

    bill = db.engine.execute(db.select([Bill]).where(and_(Bill.id == bill_id and Bill.userId == user_id))).fetchall()

    if len(bill) > 0:
        company = {}
        if bill[0].companyId is not None:
            c_list = list(filter(lambda c: c.id == bill[0].companyId, companies_list))
            if len(c_list) > 0:
                company = c_list[0]

        if request.method == 'POST':
            form = BillForm(request.form)
            if form.paid.data is None:
                form.paid.data = False
            else:
                form.paid.data = True

            if form.validate_on_submit():
                Bill.query.filter_by(id=bill[0].id).update(dict(name=form.name.data, description=form.description.data
                                                                , amount=form.amount.data, paid=form.paid.data,
                                                                categoryId=form.categoryId.data,
                                                                dueDate=form.dueDate.data,
                                                                companyId=form.companyId.data,
                                                                userId=bill[0].userId))
                db.session.commit()
                flash('Bill have been updated.')
                return redirect(url_for('bills_list'))
    flash('Bill not found.')

    return render_template('edit-bill.html', bill=bill[0], company=company, companies=companies_list,
                           categories=categories_list)


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = changePasswordFrom(request.form)
    if request.method == 'POST':
        account = db.engine.execute('Select * from accounts where email=?', current_user.email).first()
        if check_password_hash(account.password_hash, form.currentPassword.data):
            if form.validate_on_submit():
                user = current_user
                user.password_hash = generate_password_hash(form.newPassword1.data)
                db.session.add(user)
                # Account.query.filter_by(email=account.email).update(dict(password=form.newPassword1.data))
                db.session.commit()
                return redirect(url_for('index'))
        else:
            flash('your password is incorrect')

    return render_template('change-password.html', form=form)


@app.route('/add-company', methods=['GET', 'POST'])
@login_required
def new_company():
    if request.method == 'POST':
        company = Company(name=request.form["name"], phoneNumber=request.form["phoneNumber"],
                          email=request.form["email"])
        db.session.add(company)
        db.session.commit()
        flash('Company have been saved.')

    return render_template('add-company.html')


@app.route('/delete-bill/<bill_id>', methods=['GET'])
@login_required
def delete_bill(bill_id):
    user_id = db.engine.execute('Select * from users where email=?', current_user.email).fetchall()[0].id
    bill = db.engine.execute(db.select([Bill]).where(and_(Bill.id == bill_id and Bill.userId == user_id))).fetchall()
    if len(bill) > 0:
        Bill.query.filter_by(id=bill[0].id).delete()
        db.session.commit()
        return redirect(url_for('bills_list'))
    flash('Bill not found.')
    return render_template('edit-bill.html')


@app.route('/my-profile', methods=['GET'])
@login_required
def my_profile():
    firstName = db.engine.execute('Select * from users where email=?', current_user.email).fetchall()[0].firstname
    lastName = db.engine.execute('Select * from users where email=?', current_user.email).fetchall()[0].lastname
    return render_template('my-profile.html', email=current_user.email, firstName=firstName,
                           lastname=lastName)


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = editProfileForm(request.form)
    user = db.engine.execute('Select * from users where email=?', current_user.email).fetchall()[0]
    if request.method == 'POST':
        if form.validate_on_submit():
            User.query.filter_by(id=user.id).update(dict(firstname=form.firstname.data, lastname=form.lastname.data))
            db.session.commit()
            flash('Your profile has been updated.')
            return redirect(url_for('index'))

    return render_template('edit-profile.html', form=form, firstname=form.firstname.data, lastname=form.lastname.data)


@app.route('/add-category', methods=['GET', 'POST'])
@login_required
def new_category():
    if request.method == 'POST':
        category = Category(name=request.form["name"])
        db.session.add(category)
        db.session.commit()
        flash('Category have been saved.')

    return render_template('add-category.html')


@app.route('/bills-list')
@login_required
def bills_list():
    user_id = db.engine.execute('Select * from users where email=?', current_user.email).fetchall()[0].id
    query = db.select([Bill]).where(and_(Bill.userId == user_id))
    query1 = db.select([Category])
    query2 = db.select([Company])

    result = db.engine.execute(query).fetchall()
    result1 = db.engine.execute(query1).fetchall()
    result2 = db.engine.execute(query2).fetchall()

    return render_template('bills-list.html', bills=result, categories=result1, companies=result2)


@app.route('/change')
@fresh_login_required
def change():
    return '<h1>This is for fresh logins only!</h1>'


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        account = Account.query.filter_by(email=form.email.data).first()
        if form.validate_on_submit():
            if account is None:
                account = Account(email=form.email.data, password=form.password.data)
                db.session.add(account)
                user = User(firstname=form.firstName.data, lastname=form.lastName.data, email=form.email.data)
                db.session.add(user)
                db.session.commit()
                # send_email(user.email, 'Confirm your account')
                flash('You can now login.')
                return redirect(url_for('login'))
            else:
                flash("the email already in use!")

    return render_template('register.html', form=form, firstName=form.firstName.data, lastName=form.lastName.data,
                           email=form.email.data)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


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


def default_data_categories():
    return [
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


def default_data_companies():
    return [
        Company(name="Netflix", phoneNumber="1800900120", email="contact@netflix.com")
    ]


def default_data_bills():
    return [
        Bill(name="Netflix", description="Netflix Subscription", amount=45, paid=False, companyId=1, categoryId=15,
             userId=15),
        Bill(dueDate=datetime.date(2020, 10, 10), name="Netflix", description="Netflix Subscription", amount=45,
             paid=False,
             companyId=1, categoryId=15,
             userId=1),
        Bill(dueDate=datetime.date(2022, 1, 10), name="Netflix", description="Netflix Subscription", amount=45,
             paid=False,
             companyId=1, categoryId=15,
             userId=1),
        Bill(dueDate=datetime.date(2022, 1, 14), name="Netflix", description="Netflix Subscription", amount=45,
             paid=False,
             companyId=1, categoryId=15,
             userId=1),
        Bill(dueDate=datetime.date(2022, 5, 23), name="Netflix", description="Netflix Subscription", amount=45,
             paid=False,
             companyId=1, categoryId=15,
             userId=1),
        Bill(dueDate=datetime.date(2022, 7, 12), name="Netflix", description="Netflix Subscription", amount=45,
             paid=False,
             companyId=1, categoryId=15,
             userId=1),
        Bill(dueDate=datetime.date(2022, 1, 19), name="Netflix", description="Netflix Subscription", amount=45,
             paid=False,
             companyId=1, categoryId=15,
             userId=2),
        Bill(dueDate=datetime.date(2022, 1, 19), name="Netflix", description="Netflix Subscription", amount=45,
             paid=False,
             companyId=1, categoryId=15,
             userId=2),
        Bill(dueDate=datetime.date(2022, 7, 24), name="Netflix", description="Netflix Subscription", amount=45,
             paid=False,
             companyId=1, categoryId=15,
             userId=2)
    ]


if __name__ == '__main__':
    # db.engine.execute('''DROP TABLE IF EXISTS categories;''')
    # db.engine.execute('''DROP TABLE IF EXISTS companies;''')
    # db.engine.execute('''DROP TABLE IF EXISTS bills;''')
    #
    # db.create_all()
    #
    # db.session.bulk_save_objects(default_data_categories())
    # db.session.commit()

    # db.session.bulk_save_objects(default_data_companies())
    # db.session.commit()

    # db.session.bulk_save_objects(default_data_bills())
    # db.session.commit()

    app.run(debug=True)
