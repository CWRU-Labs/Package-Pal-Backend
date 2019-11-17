# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 10:15:30 2019

@author: Jacob Engelbrecht 
"""
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import mysql.connector
from google.cloud import vision, storage
import datetime
import configparser
import uuid 
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Read configuration from file.
config = configparser.ConfigParser()
config.read('config.ini')

# Configure Flasks to host web server, Cross Origin Requsts and API functionality
app = Flask(__name__)
CORS(app)
api = Api(app)

sendEmails = True

"""!!! BACKEND CLASS DEFINITIONS !!!"""
class DBConnect():
    """Class to handle connection to the Google SQL Database
    
    Connects to Google Cloud SQL Database for informationr regarding packages,
    students, and housing. 
    """
    def __init__(self):
        """Init Class using known information about server"""
        self.mydb = mysql.connector.connect(**config['mysql.connector'])
        self.cursor = self.mydb.cursor()
        
    def close(self):
        """Closes the connection to the database, good practice"""
        self.cursor.close()
        self.mydb.close()
    
    
class PackageDB(DBConnect):
    """Class that handles all CRUD relatinos with PackageDB"""
    def find(self, packID, recipient="", address="", location="", imageLoc="", description=""):
        """ Returns a Package given a unique ID
        
        Arguments
            packID: The unique ID number associated with the package.
            recipient: optional, recipient of the packge
            address: optional, listed address on the package to be found 
            location: optional, storage location of the package
            imageLoc: optional, Image location assocated with package, very optional
            description: optional, description of the package input
            
        Returns 
            A dictionary containing all package data
        """
        numID = int(packID)
        if numID > -1:
            sql = "SELECT * FROM Package WHERE packageID={packageID}".format(packageID=numID)
        else:
            if imageLoc == "":
                sql = "SELECT * FROM Package WHERE recipient='{rec}' AND \
                address='{add}' AND location='{loc}' AND description='{desc}'\
                ".format(rec=recipient, add=address, loc=location, desc=description)
            else:   
                sql = "SELECT * FROM Package WHERE recipient='{rec}' AND \
                address='{add}' AND location='{loc}' AND imageLoc='{im}'\
                ".format(rec=recipient, add=address, loc=location, im=imageLoc)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if len(results) == 0:
            return {"id":-1, 
                    "recipient":"", 
                    "address":"", 
                    "location":"", 
                    "dateTimeIn":"", 
                    "dateTimeOut":"", 
                    "completeText":"", 
                    "imageLoc":"", 
                    "description":""
                    }
        else:
            return {"id":results[0][0], 
                    "recipient":results[0][1], 
                    "address":results[0][2], 
                    "location":results[0][3], 
                    "dateTimeIn":results[0][4], 
                    "dateTimeOut":results[0][5], 
                    "completeText":results[0][6], 
                    "imageLoc":results[0][7], 
                    "description":results[0][8]
                    }
    
    def recents(self, number = 5):
        sql = "SELECT * FROM Package ORDER BY dateTimeIn DESC Limit " + str(number)
        self.cursor.execute(sql)
        resp = self.cursor.fetchall() 
        data = {}
        if len(resp) == 0:
            return {"id":-1, 
                    "recipient":"", 
                    "address":"", 
                    "location":"", 
                    "dateTimeIn":"", 
                    "dateTimeOut":"", 
                    "completeText":"", 
                    "imageLoc":"", 
                    "description":""
                    }
        else:
            index = len(resp)
            while index > 0:
                index -= 1
                pack = resp[index]
                data[pack[0]] = {"id":pack[0], 
                    "recipient":pack[1], 
                    "address":pack[2], 
                    "location":pack[3], 
                    "dateTimeIn":pack[4], 
                    "dateTimeOut":pack[5], 
                    "completeText":pack[6], 
                    "imageLoc":pack[7], 
                    "description":pack[8]
                    }
        return data 
    
    def search(self, phrase):
        sql = "SELECT * FROM Package WHERE recipient=\"" + phrase + "\""
        self.cursor.execute(sql)
        resp = self.cursor.fetchall() 
        data = {}
        if len(resp) == 0:
            return {"id":-1, 
                    "recipient":"", 
                    "address":"", 
                    "location":"", 
                    "dateTimeIn":"", 
                    "dateTimeOut":"", 
                    "completeText":"", 
                    "imageLoc":"", 
                    "description":""
                    }
        else:
            for pack in resp: 
                data[pack[0]] = {"id":pack[0], 
                    "recipient":pack[1], 
                    "address":pack[2], 
                    "location":pack[3], 
                    "dateTimeIn":pack[4], 
                    "dateTimeOut":pack[5], 
                    "completeText":pack[6], 
                    "imageLoc":pack[7], 
                    "description":pack[8]
                    }
        return data 

    
    def add(self, 
                      recipient, 
                      address, 
                      location, 
                      completeText, 
                      imageLoc, 
                      description = ""):
        """Inserts new package into the packages database 
        
        Arguments:
                recipient: the unique Student ID attribute of the recipient 
                address: The parsed address of the package
                location: The current storage location of the package
                completeText: full dump of the JSON data from Vision
                imageLoc: Cloud storage location of the image
                description (optional): other information
        """
        sql = "INSERT INTO Package (recipient, address, location, \
        dateTimeIn, completeText, imageLoc, description) VALUES \
        (%s, %s, %s, current_timestamp, %s, %s, %s)"
        values = (recipient, address, location,
                  completeText, imageLoc, description)
        self.cursor.execute(sql, values)
        self.mydb.commit()
        
    def getStudentHousing(self, name=""):
        """Finds given set of students in the Students table
        
        Arguments:
            name: optional, only returns first names which match
        
        returns:
            Two dimensional array of data, reference SQL organizatino for further info
        """
        sql = "SELECT studentID, firstName, lastName, address, city, st, zip, \
        name, room FROM Student, Housing WHERE Student.house = Housing.housingID"
        self.cursor.execute(sql)
        return(self.cursor.fetchall())
        
    def findStudent(self, studentID):
        sql = "SELECT * FROM Student WHERE studentID=\"" + studentID + "\""
        self.cursor.execute(sql)
        pack = self.cursor.fetchall() 
        if len(pack) == 0:
            return {"id":-1, 
                    "name":"", 
                    "email":""}
        else:
            pack = pack[0]
            return {"id":pack[0], 
                    "name":str(pack[1]) + str(pack[2]), 
                    "email": str(pack[0]) + "@case.edu",
                    "other": pack[3]}
        
    
class ImageProcessor():
    """Handles all image upload and processing necessary for Package Pal"""
    def __init__(self):
        """Creates standard connections for Image Processing using Google"""
        self.vision_client = vision.ImageAnnotatorClient()
        self.storage_client = storage.Client()
        self.packageDB = PackageDB()
    
    def processImage(self, name):
        """Takes the name of an already uploaded package and runs Vision AI analysis
        
        Arguments: 
            name: The name of the file or path of location in package-pal-images
                
        Return 
            Raw JSON response data from Vision AI
        """
        location = "gs://package-pal-images/" + name
        image = vision.types.Image()
        image.source.image_uri = location
        response = self.vision_client.text_detection(image=image)
        texts = response.text_annotations
        return texts
    
    def uploadImage(self, file_stream, filename, content_type):
        """Uploads a file to a given Cloud Storage bucket
        
        Arguments:
            file_stream: complete read of image data to be put in the cloud 
            filename: the name to be assigned to the given image (ideally unique)
            content_type: type of content being uploaded 
        """
        name = self.__uniqueName(filename)
        bucket = self.storage_client.get_bucket("package-pal-images")
        blob = bucket.blob(name)
        blob.upload_from_string(file_stream, content_type)
        return name
        
    def parseText(self, json):
        """Takes JSON response from Vision call and returns best matched user
        
        Arguments:
            json: The RAW JSON data from the Vision AI API call 
            
        Returns:
            the unique Student ID of who best matches the label
        """
        data = self.packageDB.getStudentHousing()
        ranks = []
        for person in data:
            ranks.append(self.__heuristic(person, self.__simplifyJSON(json)))
        maxVal = [0, 0]
        for i in range(0, len(ranks)):
            if ranks[i] > maxVal[0]:
                maxVal[0] = ranks[i]
                maxVal[1] = i
        return data[maxVal[1]][0]
    
    def handle(self, file_stream, filename, content_type):
        """Takes file upload and returns the package ID now associated with the label
            
        Really a helper method to do all the necessary processing and connections
            to Google to be able to process the data. The file comes from the
            flask calls, and then everything is attempted to be ran, but errors
            are caught so data is still returned even on failure. 
            
        Arguments: 
            ile_stream: complete read of image data to be put in the cloud 
            filename: the name to be assigned to the given image (ideally unique)
            content_type: type of content being uploaded 
        
        Returns:
            Dictionary containing status and id of new package, -1 means failure
        """
        try:
            name = self.uploadImage(file_stream, filename, "image/png")
            json = self.processImage(name)
            student = self.parseText(json)
            self.packageDB.add(student, "", "Wade Commons", self.__simplifyJSON(json),\
                               "gs://package-pal-images/" + name)
            resp = self.packageDB.find(-1, student, "", "Wade Commons",\
                                       "gs://package-pal-images/" + name)
            if resp["id"] < 0:
                return {"status": "FAILED BAD DB", "id": -1}
            else:
                return {"status": "OK", "id": str(resp["id"])}
        except:
            return {"status": "FAILED BAD Internal", "id": -1}
    
    def __heuristic(self, person, data): 
        """Looks to see how much of a match a person is to given textual data
        
        Arguments:
            person: The entire student information in array form from SQL database
            data: the simplified JSON textual data of the label 
        
        Returns:
            A value based on how much of a match the person is to the data
        """
        value = 0
        for index in range (1, len(person)):
            strForm = str(person[index])
            for word in strForm.split(" "):
                if word in data:
                    value += 1 / len(strForm.split(" "))
        return value
    
    def __simplifyJSON(self, json):
        """Takes json data from vision AI and shortens to important information
        
        Arguments:
            json: The JSON data straight out of Vision AI API
        
        Returns:
            Just the textual data found in the image without the necessary locations 
        """
        json = str(json)
        data = ""
        index = json.find("description:") + 12
        final = json.find("bounding")
        while json[index] != '\"':
            index += 1
        index += 1
        while json[index] != '\"' and index < final:
            data += json[index]
            index += 1
        return data
    
    def __uniqueName(self, filename):
        if "." in str(filename):
            name = str(filename)[:str(filename).find(".")] +\
            uuid.uuid4().hex[0:8] + str(filename)[str(filename).find("."):]
        else:
            name = filename
        return name
    
    def __hardRemove(self, packID):
        name = self.packageDB.find(packID)["imageLoc"][24:]
        bucket = self.storage_client.get_bucket("package-pal-images")
        #remove sql
        sql = "DELETE FROM Package WHERE packageID={packageID}".format(packageID=packID)
        self.packageDB.cursor.execute(sql)
        self.packageDB.mydb.commit()        
        #remove file 
        blobs = bucket.list_blobs()
        for blob in blobs:
            if blob.name == name:
                blob.delete()
  
class EmailSend():
    def __init__(self):
        self.packageDB = PackageDB()
        
    def check(self):
        pass
    
    def formEmail(self, packID):
        pack = self.packageDB.find(packID)
        resp = self.packageDB.findStudent(pack["recipient"])
        sender = 'HARLD@package-pal.appspot.com'
        recip = resp["email"]
        body = "<p>You have a package waiting at {loc}! Bring your CaseOneCard to the office to pick it up. \
                </p><p>Here are some details:</p><table><tbody><tr><th align=\"right\">Type:</th><td>{size}</td></tr><tr><th align=\"right\">\
                Delivery Date:</th><td>{arrival}</td></tr><tr><th align=\"right\">Carrier:</th><td>USPS Priority Mail</td></tr><tr><th align=\"right\"\
                >Origin:</th><td>United States</td></tr></tbody></table><p> You can always access your waiting packages and mail in your \
                <a href=\"https://housing.case.edu/myhousing\" target=\"_blank\" data-saferedirecturl=\
                \"https://www.google.com/url?q=https://housing.case.edu/myhousing&amp;source=gmail&amp;ust=1574113999646000&amp;usg=AFQjCNEQ9Z9It7YAe6Tu4smZca2gkFIP5w\">\
                myHousing</a>.</p>".format(size="Box", arrival=str(pack["dateTimeIn"]), loc=str(pack["imageLoc"]))
        return Mail(from_email= sender,
                    to_emails=recip,
                    subject='[HARLD] You\'ve received a package!',
                    html_content=body)
        
    def sendEmail(self, packID):
        message = self.formEmail(packID)
        try:
            sg = SendGridAPIClient(config['SendGrid']['Key'])
            sg.send(message)
            return True
        except:
            return False

def emails(secure):
    global sendEmails
    secure = int(secure)
    data = {}
    if secure == 2021:
        sendEmails = not sendEmails
        data["status"] = "OK"
        data["sending"] = sendEmails
    else:
        data["status"] = "Incorrect Key"
    return data 

"""!!! API CLASSES NEEDED FOR RESTFUL SERVER !!!"""
class Package(Resource):
    """Class to handle queries for singular known packages"""
    def get(self, packID):
        """Method which handles the RESTful response 
        
        Uses connection to the SQL database for getting package information
        
        Arguments:
            packID: the unique package ID to be returned 
            
        Returns:
            Package information returned in the form of JSON
        """
        db = PackageDB()
        return jsonify(db.find(packID))
    
class Recents(Resource):
    def get(self, packs):
        db = PackageDB()
        return jsonify(db.recents(packs))
    
class Search(Resource):
    def get(self, phrase):
        db = PackageDB()
        return jsonify(db.search(phrase))

class Test(Resource):
    """Class to test the running of backend server"""
    def get(self):
        """Returns the status of the server, including time to check update"""
        return jsonify(status="ok", version="1.0", time=str(datetime.datetime.now().time()))
    
class Employees_Name(Resource):
    """Class to handle """
    def get(self, employee_id):
        return jsonify(username="Jason", email="jd4", id="jd45")
    
class Email(Resource):
    """Class to handle """
    def get(self, secure):
        return jsonify(emails(secure))


"""!!! API ROUTE DEFINITIONS !!!"""
api.add_resource(Package, '/package/<packID>') # Route_1
api.add_resource(Test, '/test') # Route_2
api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3
api.add_resource(Recents, '/recents/<packs>') # Route_4
api.add_resource(Search, '/search/<phrase>') # Route_5
api.add_resource(Email, '/email/<secure>') # Route_6

@app.route('/uploader', methods = ['POST', 'GET'])
@cross_origin(origin='*')
def upload_file():
    """ Handles image uploads from general internet 
    
    Takes in a request element given from flask which needs to come from a POST
        request which needs to contain a form with an element 'file' associated
        with the binary of an image which is to be processed. The image needs to 
        be in the format of .jpg, .jpeg, or .png
        
    Returns:
        The status of the image processing in addition to package ID associated with the upload
    """
    if request.method == 'POST':
        # check if the post request has the file part
        if "file" not in request.files:
            dat = request.form.to_dict(flat=True)
            inf = request.files.to_dict(flat=True)
            return jsonify(status="FAILED 1", form=str(dat.keys()),\
                           files=str(inf.keys()), other=str(request.files.get('file')), id="-1")
        file = request.files['file']
        if file.filename == '' or \
            (".png" not in file.filename and ".jpeg" not in file.filename and ".jpg" not in file.filename):
            return jsonify(status="FAILED 2", id="-1")
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        proc = ImageProcessor()
        return jsonify(proc.handle(file.read(), file.filename, file.content_type))
        
    
"""!!! MAIN METHOD !!!"""
if __name__ == '__main__':
    #Start Flask Server
    app.run(port=8080, debug=True, use_reloader=False)
    #print("Hello World")
