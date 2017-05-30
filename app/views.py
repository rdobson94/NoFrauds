"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
import os
import io
import re
import string
import textract,textrazor
from app import app
from flask import render_template, request, redirect, url_for, flash, session, abort, jsonify
from werkzeug.utils import secure_filename
import textract
import itertools
from google import google
from bs4 import BeautifulSoup
import ast
import textrazor
import re
import string
import validators
import os
import requests
from difflib import SequenceMatcher
import numpy as np
from PyDictionary import PyDictionary
import difflib
from app.algorithm import webScraper


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'docx', 'rtf', 'doc'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS   
    

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")




@app.route('/add-file', methods=['POST', 'GET'])
def add_file():
    file_folder = "app/static/uploads/"
    if request.method=='POST':
        textarea=request.form['textarea']
        if textarea and textarea!="": 
            scraper = webScraper(textarea)
            flash("Processing")

        else:
            file = request.files['file']
            if file and not allowed_file(file.filename):
                flash('Incompatible Document Type, Try again')
            else:
                filename = secure_filename(file.filename)
                file.save(os.path.join(file_folder, filename))
                textarea=textract.process(file_folder+filename)
            
                flash("File Uploaded Successfully")
                
                
        #return redirect(url_for("results"))    
        return render_template("results.html",credibility=scraper[11], subjectmatches = scraper[12] , inputcategory = scraper[14], cat_score = scraper [3],
        siteurl = scraper[5], phrasematches = scraper[10], matchingphrases = scraper[16], matchingsubjects = scraper[15],
        entitymatches = scraper [13], matchingentities = scraper[18], phraselist = scraper[1], entitylist = scraper[0], sublist = scraper[2], maincategory =scraper[4],
        urlphraselist = scraper [7], urlentitylist = scraper [8], urlsublist = scraper[9], urlmaincategory = scraper[6], scraperlen = len(scraper))
            


    return render_template('add_file.html')



    
@app.route('/results')
def results():
    return render_template("results.html")

#@app.route('/login', methods=['POST', 'GET'])
#def login():
#    error = None
#    if request.method == 'POST':
#        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
#            error = 'Invalid username or password'
#        else:
#            session['logged_in'] = True
#            
#            flash('You were logged in')
#            return redirect(url_for('add_file'))
#    return render_template('login.html', error=error)

#@app.route('/logout')
#def logout():
#    session.pop('logged_in', None)
#    flash('You were logged out')
#    return redirect(url_for('home'))


###
# The functions below should be applicable to all Flask apps.
###



@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
