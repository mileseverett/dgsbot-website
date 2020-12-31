import os
from flask import Flask, render_template, escape, request, redirect, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

import jsonFunctions
import winterfaceDB

application = Flask(__name__)

SECRET_KEY = os.urandom(32)
application.config['SECRET_KEY'] = SECRET_KEY

class MyForm(FlaskForm):
    player1 = StringField('player1', validators=[DataRequired()])
    player2 = StringField('player2', validators=[DataRequired()])
    player3 = StringField('player3', validators=[DataRequired()])
    player4 = StringField('player4', validators=[DataRequired()])
    player5 = StringField('player5', validators=[DataRequired()])
    time = StringField('time', validators=[DataRequired()])
    theme = SelectField(
        'Theme', choices=[('Frozen', 'Frozen'), ('Abandoned 1', 'Abandoned 1'), ('Furnished', 'Furnished'),('Abandoned 2', 'Abandoned 2'),('Occult', 'Occult'),('Warped', 'Warped')]
    )

@application.route("/")
def index():

    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")

    if app_name:
        return f"Hello from {app_name} running in a Docker container behind Nginx!"

    return "Hello from Flask"

@application.route("/<wintNumber>", methods=('GET','POST'))
def eb(wintNumber):
    form = MyForm()
    # data = getData(wintNumber)
    secretValue = wintNumber[-32:]
    floorID = wintNumber[:-32]
    testVariable = "yea"
    # ---------- TODO debugging for 404 page, i added in this check to 404 instead of 500 fail.. i think we need a more robust way to handle this? ------------#
    # -- Maybe a DB check that's like hey is this URL in the table? If not, server error? Not totally robust if website if used for more stuff later.. -- #
    if not floorID:
        abort(404)
    data = winterfaceDB.retrieveFloor2(floorID)
    secret = winterfaceDB.retrieveFloor(floorID)
    wintNumberPath = wintNumber + ".png"
    full_filename = os.path.join(application.config['UPLOAD_FOLDER'], wintNumberPath)
    if request.method == 'GET':
        form = populateForm(form,data)
        return render_template('index.html',title="DGS Highscores",testVariable=data,imageUrl=data[0][8],defaultValue=testVariable,form=form)
    elif request.method == 'POST':
        winterfaceDB.updateFloor(floorID,form.player1.data,form.player2.data,form.player3.data,form.player4.data,form.player5.data,form.time.data,form.theme.data)
        winterfaceDB.updateSubmissionStatus(floorID,1)
        return render_template('index.html',title="DGS Highscores",testVariable="Details updated!",imageUrl=data[0][8],defaultValue=testVariable,form=form)

@application.route("/adminPage",methods=('GET','POST'))
def adminPage():
    data = winterfaceDB.retrieveCompleted(1)
    floors = []
    for x in data:
        floors.append(winterfaceDB.retrieveFloor2(x[0]))
    return render_template('adminPage.html',options=floors)

def getData(wintNumber):
    wintNumberPath = "app/jsonFiles/" + wintNumber + ".json"
    print (wintNumberPath)
    return jsonFunctions.loadJSON(wintNumberPath)

def dumpData(wintNumber,data):
    wintNumberPath = "app/jsonFiles/" + wintNumber + ".json"
    jsonFunctions.dumpJSON(wintNumberPath,data)
    return

def populateForm(form,data):
    form.player1.data = data[0][1]
    form.player2.data = data[0][2]
    form.player3.data = data[0][3]
    form.player4.data = data[0][4]
    form.player5.data = data[0][5]
    form.time.data = data[0][7]
    form.theme.data = data[0][6]
    return form

@application.route("/success", methods=('GET','POST'))
def success():
    return "All done!"

PEOPLE_FOLDER = os.path.join('static', 'images')

application.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

@application.errorhandler(404)
def page_not_found(e):
    return render_template('404page.html'), 404

@application.errorhandler(500)
def application_error(e):
    return render_template('500page.html'), 500

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = False
    application.run()