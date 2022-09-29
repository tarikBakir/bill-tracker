from flask_wtf import Form
from wtforms import StringField, SubmitField, FloatField, DateField, IntegerField
from wtforms.validators import InputRequired, Length


class BillForm(Form):
    name = StringField('name',
                       validators=[InputRequired(),
                                   Length(max=64)])
    description = StringField('description',
                              validators=[InputRequired(),
                                          Length(max=64)])
    paid = StringField('paid',
                       validators=[InputRequired()])

    amount = FloatField('amount',
                        validators=[InputRequired()])

    dueDate = DateField('dueDate',
                        validators=[InputRequired()])

    companyId = IntegerField('id')

    categoryId = IntegerField('categoryId',
                              validators=[InputRequired()])

    submit = SubmitField('submit')

    def validate_on_submit(self):
        return True
