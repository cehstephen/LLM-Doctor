import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, validators
from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail, Message
import datetime

import secrets  # To generate secure activation tokens
from apscheduler.schedulers.background import BackgroundScheduler

# import openai
from decouple import config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL') 
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['MAIL_SERVER'] = config('MAIL_SERVER')
app.config['MAIL_PORT'] = 26
app.config['MAIL_USERNAME'] = config('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = config('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True

app.config['SESSION_TYPE'] = config('SESSION_TYPE') 


# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='LLM Admin Dashboard', template_mode='bootstrap3')


db = SQLAlchemy(app)
mail = Mail(app)


class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ai_model_name = db.Column(db.String(20), default='gpt-3.5-turbo')
    system_message_desc = db.Column(db.Text, nullable=True)
    assistant_message_desc = db.Column(db.Text, nullable=True)
    user_message_desc = db.Column(db.Text, nullable=False)
    search_result = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), default='gpt-3.5-turbo')
    user_name = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='active')
    access_role = db.Column(db.String(20), default='user')
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class PatientMedicalHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_id = db.Column(db.String(30), nullable=True)
    visited_dept = db.Column(db.String(40), nullable=True)
    patient_case_desc = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    creator = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff = db.relationship('User', backref=db.backref('patientmedicalhistory', lazy=True))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    
admin.add_view(ModelView(SearchHistory, db.session))
admin.add_view(ModelView(PatientMedicalHistory, db.session))
admin.add_view(ModelView(User, db.session))

@app.route('/', methods=['GET', 'POST'])
def index():
    county = "Teesside"
    new_search = SearchHistory()

    llm_legacy_models = ["gpt-3.5-turbo-0301", "gpt-3.5-turbo-16k-0613", "gpt-4-32k-0314", "gpt-4-0314", ]
    llm_models = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-4-32k-0613", "gpt-4-0613", "gpt-4-32k", "gpt-4", "gpt-4-vision-preview", "gpt-4-1106-preview"]

    if request.method == "POST":
        import openai
        # Initialize your OpenAI API key
        openai.api_key = config('MY_OPEN_AI_SECRET_KEY')
        URL = "https://api.openai.com/v1/chat/completions"

        healthInputCase = request.form['healthInputCase']
        model_name = request.form['desired_model']
        
        #Check if the user choose a valid model
        if model_name in llm_models:
            ai_model_name = model_name
        else:
            ai_model_name = 'gpt-3.5-turbo'
        
        if healthInputCase:
            try:
                payload = {
                "model": "gpt-4-1106-preview",
                "temperature" : 1.0,
                "messages" : [
                    {"role": "system", "content": f"You are providing assisted medical advice to experienced medical professionals. Limit the lenght of output to 200 words."},
                    {"role": "assistant", "content": f"Use medical terminologies in your response, ensure you give reasons for each advice you provide."},
                    {"role": "user", "content": f"{healthInputCase} "},
                    ]
                }

                headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai.api_key}"
                }

                response = requests.post(URL, headers=headers, json=payload)
                response = response.json()

                # Return the response to the user
                with open("med_advice.txt", "wt") as answers:
                    answers.writelines(response['choices'][0]['message']['content'])
                final_data = response['choices'][0]['message']['content'] #jsonify({'chat_response': chat_response})
                
                new_health_search = SearchHistory(
                search_result=final_data,
                ai_model_name=ai_model_name,
                user_message_desc = healthInputCase)

                db.session.add(new_health_search)
                db.session.commit()
                return jsonify({'output': final_data })
            except:
                return jsonify({'output':'Opps! Something went wrong. Make sure your secrete key is correct and valid.'})
        return jsonify({'output' : 'Missing data. Please enter some data and search again.'})
    
    return render_template('new.html', app_county=county, form=new_search, valid_models=llm_models)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
