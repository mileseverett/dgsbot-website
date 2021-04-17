import os
from flask import Flask, render_template, request, abort
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, ValidationError
import re
import requests
from PIL import Image
import io

import winterfaceDB

application = Flask(__name__)

SECRET_KEY = os.urandom(32)
application.config['SECRET_KEY'] = SECRET_KEY

class MyForm(FlaskForm):
    def validateRSN(FlaskForm, field, message = None):
        rsn = field.data
        if len(rsn) < 1 or len(rsn) > 12:
            raise ValidationError('RSN must be between 1 and 12 characters long.')

        if not rsn.isalnum() or "_" in rsn or "-" in rsn:
            raise ValidationError('RSN cannot contain special characterss.')
    
        return True
    
    def validateTime(FlaskForm, field, message = None):
        timeData = field.data
        if len(timeData) != 8:
            raise ValidationError('Time must be 8 characters, in the form: xx:yy:zz. Include leading zeros and commas.')

        if re.search('[a-zA-Z]', timeData):
            raise ValidationError('Time cannot have letters in it. Submit in the form: xx:yy:zz. Include leading zeros and commas.')
    
        return True
        
    player1 = StringField('player1', validators=[DataRequired(), validateRSN])
    player2 = StringField('player2', validators=[DataRequired(), validateRSN])
    player3 = StringField('player3', validators=[DataRequired(), validateRSN])
    player4 = StringField('player4', validators=[DataRequired(), validateRSN])
    player5 = StringField('player5', validators=[DataRequired(), validateRSN])
    time = StringField('time', validators=[DataRequired(), validateTime])
    theme = SelectField(
        'Theme', choices=[('Frozen', 'Frozen'), ('Abandoned 1', 'Abandoned 1'), ('Furnished', 'Furnished'),('Abandoned 2', 'Abandoned 2'),('Occult', 'Occult'),('Warped', 'Warped')]
    )

@application.route("/")
def index():
    return "Landing page that needs some buttons... :)"

@application.route("/hiscore", methods=('GET','POST'))
def highscore():
    print ("Printing")
    frozen = winterfaceDB.grabTopNByTheme("Frozen", tableType = "overall")
    ab1 = winterfaceDB.grabTopNByTheme("Abandoned 1", tableType = "overall")
    furn = winterfaceDB.grabTopNByTheme("Furnished", tableType = "overall")
    ab2 = winterfaceDB.grabTopNByTheme("Abandoned 2", tableType = "overall")
    occ = winterfaceDB.grabTopNByTheme("Occult", tableType = "overall")
    warp = winterfaceDB.grabTopNByTheme("Warped", tableType = "overall")
    overall = winterfaceDB.grabTopNOverall(10, tableType = "overall")
    people = winterfaceDB.grabTopNAppearances(100, tableType = "overall")
    return render_template('hiscores.html',overall=overall,frozen=frozen,ab1=ab1,furn=furn,ab2=ab2,occ=occ,warp=warp,people=people)

@application.route("/hiscore/monthly", methods=('GET','POST'))
def monthlyhighscore():
    print ("Printing")
    frozen = winterfaceDB.grabTopNByTheme("Frozen", tableType = "monthly")
    ab1 = winterfaceDB.grabTopNByTheme("Abandoned 1", tableType = "monthly")
    furn = winterfaceDB.grabTopNByTheme("Furnished", tableType = "monthly")
    ab2 = winterfaceDB.grabTopNByTheme("Abandoned 2", tableType = "monthly")
    occ = winterfaceDB.grabTopNByTheme("Occult", tableType = "monthly")
    warp = winterfaceDB.grabTopNByTheme("Warped", tableType = "monthly")
    overall = winterfaceDB.grabTopNOverall(5, tableType = "monthly")
    people = winterfaceDB.grabTopNAppearances(100, tableType = "monthly")
    return render_template('monthlyHiscores.html',overall=overall,frozen=frozen,ab1=ab1,furn=furn,ab2=ab2,occ=occ,warp=warp,people=people)

@application.route("/hiscore/<wintNumber>", methods=('GET','POST'))
def eb(wintNumber=""):
    form = MyForm()
    print (wintNumber)


    secretValue = wintNumber[-32:]
    floorID = wintNumber[:-32]
    # TODO debugging for 404 page, i added in this check to 404 instead of 500 fail.. i think we need a more robust way to handle this?
    # Maybe a DB check that's like hey is this URL in the table? If not, server error? Not totally robust if website is used for more stuff later.. #
    if not floorID:
        abort(404)
    data = winterfaceDB.retrieveFloorRaw(floorID)
    secret = winterfaceDB.retrieveFloorStatus(floorID)
    wintNumberPath = wintNumber + ".png"
    fullFilename = os.path.join(application.config["UPLOAD_FOLDER"], wintNumberPath)
    print (fullFilename)
    checkForImage(fullFilename,data[0])
    fullFilename = "/" + fullFilename

    if request.method == 'GET':
        form = populateForm(form,data[0])
        return render_template('index.html', title="DGS Highscores", testVariable=data, imageUrl=fullFilename, form=form)
    elif request.method == 'POST':
        winterfaceDB.updateFloor(floorID, form.player1.data, form.player2.data, form.player3.data, form.player4.data, form.player5.data, form.time.data, form.theme.data)
        winterfaceDB.updateSubmissionStatus(floorID,1)
        return render_template('hiscoreCompleted.html')

def checkForImage(fullFilename,data):
    if os.path.exists(fullFilename) == True:
        return
    else:
        print ("Image does NOT exist")
        r = requests.get(data[8])
        image = Image.open(io.BytesIO(r.content))
        image.save(fullFilename)
        return


def populateForm(form,data):
    form.player1.data = data[1]
    form.player2.data = data[2]
    form.player3.data = data[3]
    form.player4.data = data[4]
    form.player5.data = data[5]
    form.time.data = data[7]
    form.theme.data = data[6]
    return form

@application.route("/hiscore/admin/<pageID>",methods=('GET','POST'))
def adminPage(pageID):
    secretValue = pageID[-32:]
    sessionID = pageID[:-32]
    if not sessionID:
        abort(404)
    sessionData = winterfaceDB.retrieveAdminPageRaw(sessionID)
    print (sessionData)
    if sessionData[0][1] == secretValue:
        pass
    else:
        abort(404)

    if request.method == "GET":
        data = winterfaceDB.retrieveCompleted()
        floors = []
        return render_template('adminPage.html',options=data)

    elif request.method == "POST":
        values = (request.form.to_dict())
        if "accept" in values.values():
            data = winterfaceDB.retrieveCompleted()
            for x in data:
                if values[str(x[0])] == "accept":
                    winterfaceDB.uploadToAcceptedDB(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[10])
                    winterfaceDB.updateAdminStatus(x[0])
                else: 
                    print (data,"was not accepted")
        data = winterfaceDB.retrieveCompleted()
        print (values)
        return render_template('adminCompleted.html')

@application.route("/success", methods=('GET','POST'))
def success():
    return "All done!"

images = os.path.join('static', 'images')

application.config['UPLOAD_FOLDER'] = images

@application.errorhandler(404)
def page_not_found(e):
    return render_template('404page.html'), 404

@application.errorhandler(500)
def application_error(e):
    return render_template('500page.html'), 500

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()