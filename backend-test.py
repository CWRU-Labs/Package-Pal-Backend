# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 11:42:47 2019

@author: jacob
"""

import json
import mysql.connector
import datetime
import configparser
import uuid 

"""!!! Necessary for Testing !!!"""
import unittest 
class TestStringMethods(unittest.TestCase):

    def test_findUser(self):
        im = ImageProcessor()
        self.assertEqual(im.parseText(getJSON("data.json")), 'jse41')
        self.assertEqual(im.parseText(getJSON("uri.json")), 'smk191')
        
    def test_simplifyJSON(self):
        im = ImageProcessor()
        self.assertTrue("locale" not in im.simplifyJSON(getJSON("data.json")))
        self.assertTrue("bounding" not in im.simplifyJSON(getJSON("data.json")))
        self.assertTrue(len(getJSON("data.json")) > len(im.simplifyJSON(getJSON("data.json"))))
        
    def test_uniqueName(self):
        im = ImageProcessor()
        self.assertNotEqual(im.uniqueName("jacob.jpg"), im.uniqueName("jacob.jpg"))
        self.assertGreater(len(im.uniqueName("jacob.jpg")), len("jacob.jpg"))
        self.assertTrue(".png" in im.uniqueName("jacob.png"))
        self.assertEqual(im.uniqueName("jacob"), im.uniqueName("jacob"))
        
    def test_heuristic(self):
        im = ImageProcessor()
        a = getInfo()
        self.assertAlmostEqual(3.5, im.heuristic(a[3], im.simplifyJSON(getJSON("data.json"))))
        self.assertAlmostEqual(7.5, im.heuristic(a[2], im.simplifyJSON(getJSON("data.json"))))
        self.assertAlmostEqual(3.0, im.heuristic(a[1], im.simplifyJSON(getJSON("data.json"))))
        self.assertAlmostEqual(5.5, im.heuristic(a[0], im.simplifyJSON(getJSON("data.json"))))
        
        self.assertAlmostEqual(3.75, im.heuristic(a[3], im.simplifyJSON(getJSON("uri.json"))))
        self.assertAlmostEqual(4.75, im.heuristic(a[2], im.simplifyJSON(getJSON("uri.json"))))
        self.assertAlmostEqual(7.5, im.heuristic(a[1], im.simplifyJSON(getJSON("uri.json"))))
        self.assertAlmostEqual(4.75, im.heuristic(a[0], im.simplifyJSON(getJSON("uri.json"))))
        
        

def jsonify(info):
    return json.dumps(info)

def getJSON(path):
    with open(path) as json_file:
        file = json_file.read()
    return file

def getInfo():
    jacob = ["jse41", "Jacob", "Engelbrecht", "44106", "OH", "Cleveland", "House 3", "1681 E 116 St.", "133 A"]
    jason = ["jdr145", "Jason", "Richards", "44106", "OH", "Cleveland", "House 3", "1681 E 116 St.", "133 B"]
    uri = ["smk191", "Uri", "Johson", "44106", "OH", "Cleveland Heights", "Glaser House", "11900 Carlton Rd", "220 D"]
    ryan = ["mxh740", "Ryan", "Upson", "44106", "OH", "Cleveland", "Cutler House", "1616 E 115 St.", "420"]
    data = [jason, uri, jacob, ryan]
    return data 

"""!!! Backend testing material !!!"""

# Read configuration from file.
config = configparser.ConfigParser()
config.read('config.ini')


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
        
        
    
class ImageProcessor():
    """Handles all image upload and processing necessary for Package Pal"""
    def __init__(self):
        """Creates standard connections for Image Processing using Google"""
        """??? self.vision_client = vision.ImageAnnotatorClient() ???"""
        """??? self.storage_client = storage.Client() ???"""
        """??? self.packageDB = PackageDB() ???"""
    
    """???
    def processImage(self, name):
        ???""""""Takes the name of an already uploaded package and runs Vision AI analysis
        
        Arguments: 
            name: The name of the file or path of location in package-pal-images
                
        Return 
            Raw JSON response data from Vision AI
        """"""???
        location = "gs://package-pal-images/" + name
         image = vision.types.Image()
        image.source.image_uri = location
        response = self.vision_client.text_detection(image=image)
        texts = response.text_annotations
        return texts
    
    def uploadImage(self, file_stream, filename, content_type):
        ???""""""Uploads a file to a given Cloud Storage bucket
        
        Arguments:
            file_stream: complete read of image data to be put in the cloud 
            filename: the name to be assigned to the given image (ideally unique)
            content_type: type of content being uploaded 
        """"""???
        name = self.__uniqueName(filename)
        bucket = self.storage_client.get_bucket("package-pal-images")
        blob = bucket.blob(name)
        blob.upload_from_string(file_stream, content_type)
        return name
    ???"""
        
    def parseText(self, json):
        """Takes JSON response from Vision call and returns best matched user
        
        Arguments:
            json: The RAW JSON data from the Vision AI API call 
            
        Returns:
            the unique Student ID of who best matches the label
        """
        data = getInfo()
        ranks = []
        for person in data:
            ranks.append(self.heuristic(person, self.simplifyJSON(json)))
        maxVal = [0, 0]
        for i in range(0, len(ranks)):
            if ranks[i] > maxVal[0]:
                maxVal[0] = ranks[i]
                maxVal[1] = i
        return data[maxVal[1]][0]
    
    """???
    def handle(self, file_stream, filename, content_type):
        ???""""""Takes file upload and returns the package ID now associated with the label
            
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
        """"""???
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
    ???"""
    
    def heuristic(self, person, data): 
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
    
    def simplifyJSON(self, json):
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
    
    def uniqueName(self, filename):
        if "." in str(filename):
            name = str(filename)[:str(filename).find(".")] +\
            uuid.uuid4().hex[0:8] + str(filename)[str(filename).find("."):]
        else:
            name = filename
        return name
        
  

"""!!! API CLASSES NEEDED FOR RESTFUL SERVER !!!"""
class Package():
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

class Test():
    """Class to test the running of backend server"""
    def get(self):
        """Returns the status of the server, including time to check update"""
        return jsonify(status="ok", version="1.0", time=str(datetime.datetime.now().time()))
    
class Employees_Name():
    """Class to handle """
    def get(self, employee_id):
        return jsonify(username="Jason", email="jd4", id="jd45")

if __name__ == '__main__':
    print("Testing has Begun")
    unittest.main()