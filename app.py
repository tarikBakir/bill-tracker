#!/usr/bin/env python
from urllib.parse import urlparse, urljoin
import jinja2.exceptions
from flask import Flask, render_template, session, request, redirect, url_for, flash, make_response
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, \
    fresh_login_required, UserMixin, login_manager
from itsdangerous import URLSafeTimedSerializer, SignatureExpired  # after a time the user will logged out automaticlly
from sqlalchemy import insert, and_
from werkzeug.security import check_password_hash
import datetime
from database import db
from models.account import Account
from models.account_preferences import Account_Preference
from models.address import Address
from models.notification import Notification
from models.company import Company
from models.user import User
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
    app.app_context().push()
    #
    login_manager.init_app(app)

    db.init_app(app)

    return app


@login_manager.user_loader
def load_user(email):
    return Account.query.get(email)


login_manager.login_message = 'the email or password are incorrect.'

app = create_app()

serializer = URLSafeTimedSerializer(app.secret_key)
login_manager.login_view = 'login'
login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = 'You need to login again!'


def is_safe_url(target):  # its safer url when its redirected
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/profile')
@login_required
def profile():
    return f'<h1>You are in the profile, {current_user.email}.</h1>'


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
            resp = make_response(render_template('login.html'))
            resp.set_cookie('user_email', form.email.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid email or password.')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged Out.')
    return redirect(url_for('profile'))


@app.route('/')
@login_required
def index():
    monthlyBillsAmount = db.engine.execute(
        'SELECT SUM(amount) AS total FROM bills WHERE dueDate > DATETIME("now", "-31 day") AND paid = 0').fetchall()

    paidMonthlyBillsAmount = db.engine.execute(
        'SELECT SUM(amount) AS total FROM bills WHERE dueDate > DATETIME("now", "-31 day") AND paid = 1').fetchall()

    billsAmountByMonth = db.engine.execute(
        "SELECT b.userId,strftime('%m', b.dueDate) AS 'Month',sum(b.amount) AS 'monthlyPayment' ,count(b.id) AS 'number Of Bills' from bills AS b where date('now')-date(b.dueDate)<=1 AND userId = 2 group by b.userId,Month ORDER BY Month ASC;").fetchall()

    billsAmountByMonth_amountsMapped = list(map(lambda b: b.monthlyPayment, billsAmountByMonth))

    topFiveCategories = db.engine.execute(
        'select c.name as category, count(b.id) as NumberOfBills from categories as c inner join bills as b on c.id = b.categoryId group by c.name order by NumberOfBills DESC limit 5').fetchall()

    topFiveCategories_names = list(map(lambda b: b.category, topFiveCategories))
    topFiveCategories_amount = list(map(lambda b: b.NumberOfBills, topFiveCategories))

    user = db.engine.execute('Select * from users where email=?', current_user.email).fetchall()[0]
    return render_template('index.html',
                           user_name=user.firstname + ' ' + user.lastname,
                           totalUnpaid=str(monthlyBillsAmount[0].total), totalPaid=str(paidMonthlyBillsAmount[0].total),
                           billsAmountByMonth=billsAmountByMonth_amountsMapped,
                           topFiveCategories_names=topFiveCategories_names,
                           topFiveCategories_amount=topFiveCategories_amount)


@app.route('/blank')
@login_required
def blank():
    return render_template('blank.html')


@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')


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
        # if bill.paid is None or bill.paid is False:
        #     bill.paid = 'off'

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
    result = db.engine.execute(query).fetchall()
    return render_template('bills-list.html', bills=result)


@app.route('/change')
@fresh_login_required
def change():
    return '<h1>This is for fresh logins only!</h1>'


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
             userId=1),
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
    db.engine.execute('''DROP TABLE IF EXISTS categories;''')
    db.engine.execute('''DROP TABLE IF EXISTS companies;''')
    db.engine.execute('''DROP TABLE IF EXISTS bills;''')

    db.create_all()

    db.session.bulk_save_objects(default_data_categories())
    db.session.commit()

    db.session.bulk_save_objects(default_data_companies())
    db.session.commit()

    db.session.bulk_save_objects(default_data_bills())
    db.session.commit()

    app.run(debug=True)
