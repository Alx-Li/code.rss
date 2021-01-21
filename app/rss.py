from flask import Flask, redirect, url_for, render_template, Blueprint, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField, TextAreaField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email
from flask_pymongo import PyMongo
from datetime import datetime
import email_validator
import yagmail
import smtplib


app = Flask(__name__,
            template_folder='templates',  # Name of html file folder
            static_folder='static'  # Name of directory for static files)
            )
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'randomkey'

# database name is contact_form, user name is admin password is rhsprogrammingclub
mongo = PyMongo(
    app, uri="mongodb+srv://admin:rhsprogrammingclub@code-rss.pdhzz.mongodb.net/contact_form?retryWrites=true&w=majority")


class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message')
    department = SelectField('Department', choices=[("Grade 8", "8"), ("Grade 9", "9"), (
        "Grade 10", "10"), ("Grade 11", "11"), ("Grade 12", "12")], validators=[DataRequired()])
    submit = SubmitField('Submit')
 
def log_information(name, email, message, department, subtime):
    return {"name": name, "email": email, "message": message, "department": department, "submit_time": subtime}

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    return render_template("contact.html", form=form)

# ---------contact page form code-----------------
@app.route("/submit", methods=['GET', 'POST'])

def submit():
# ----------------------- mongo db ----------------------    
    entry_collection = mongo.db.entries
    form = ContactForm()
    if request.method == 'POST':
        #now = datetime.now()
        utc = datetime.utcnow()
        #current_time = now.strftime("%d/%m/%Y") +" "+ now.strftime("%H:%M:%S")
        entry_collection.create_index("submit_time", expireAfterSeconds = 604800)
        entry_collection.insert_one( 
            {"name": form.name.data, "email": form.email.data, "department": form.department.data, "message": form.message.data, "submit_time": utc} 
            )
#------------------------yagmail------------------------------------------------------------------------
        #initializing the server connection for yagmail
        mail = yagmail.SMTP( user='exec.rhs.code@gmail.com', password='BruhMoment123', host='smtp.gmail.com') #should add oauth
        #sending the email
        mail.send(
            to='exec.rhs.code@gmail.com', 
            subject='Form Entry', 
            contents= [
                {"name": form.name.data, "email": form.email.data, "department": form.department.data, "message": form.message.data, "submit_time": utc}
            ]
        )

        form.name.data = None
        form.email.data = None
        form.message.data = None
        form.department.data = None

        return "<h1 style = 'display:flex; text-align:center; margin:auto;'>Response Submitted</h1>"


if __name__ == "__main__":
    app.run(debug=True)

