from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, validators, StringField, SubmitField

from .api import fetch_articles, get_keywords


bp = Blueprint('index', __name__, url_prefix='/')

class FactForm(FlaskForm):
    text = TextAreaField('Text:', validators=[validators.required()])

    def validate(self):
        text = self.text.data
        if text != "Enter text to Fact Check...":
            print("Enter text")
        return True



@bp.route('/', methods=['POST','GET'])
def fact_checker():
    form = FactForm()
    if form.validate():
        text = form.text.data
        articles = fetch_articles(text)
        print(form.errors)
        return render_template('index.html', form=form, search_results=articles)
    return render_template('index.html', form=form)
