# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 11:50:08 2019

@author: Jacob Engelbrecht 
"""

import main
import unittest 
import os 
import random
from PIL import Image
from io import BytesIO
# Imports the Google Cloud client library
from google.cloud import storage

class TestStringMethods(unittest.TestCase):

    def test_findUser(self):
        im = serv.ImageProcessor()
        self.assertEqual(im.parseText(getJSON("data.json"))[0], 'jse41')
        self.assertEqual(im.parseText(getJSON("uri.json"))[0], 'smk191')
        
    def test_simplifyJSON(self):
        im = serv.ImageProcessor()
        self.assertTrue("locale" not in im._ImageProcessor__simplifyJSON(getJSON("data.json")))
        self.assertTrue("bounding" not in im._ImageProcessor__simplifyJSON(getJSON("data.json")))
        self.assertTrue(len(getJSON("data.json")) > len(im._ImageProcessor__simplifyJSON(getJSON("data.json"))))
        
    def test_uniqueName(self):
        im = serv.ImageProcessor()
        for _ in range(100):
            self.assertNotEqual(im._ImageProcessor__uniqueName("jacob.jpg"), im._ImageProcessor__uniqueName("jacob.jpg"))
        self.assertGreater(len(im._ImageProcessor__uniqueName("jacob.jpg")), len("jacob.jpg"))
        self.assertTrue(".png" in im._ImageProcessor__uniqueName("jacob.png"))
        self.assertEqual(im._ImageProcessor__uniqueName("jacob"), im._ImageProcessor__uniqueName("jacob"))
        
    def test_heuristic(self):
        im = serv.ImageProcessor()
        a = getInfo()
        self.assertAlmostEqual(3.5, im._ImageProcessor__heuristic(a[3], im._ImageProcessor__simplifyJSON(getJSON("data.json"))))
        self.assertAlmostEqual(7.5, im._ImageProcessor__heuristic(a[2], im._ImageProcessor__simplifyJSON(getJSON("data.json"))))
        self.assertAlmostEqual(3.0, im._ImageProcessor__heuristic(a[1], im._ImageProcessor__simplifyJSON(getJSON("data.json"))))
        self.assertAlmostEqual(5.5, im._ImageProcessor__heuristic(a[0], im._ImageProcessor__simplifyJSON(getJSON("data.json"))))
        
        self.assertAlmostEqual(3.75, im._ImageProcessor__heuristic(a[3], im._ImageProcessor__simplifyJSON(getJSON("uri.json"))))
        self.assertAlmostEqual(4.75, im._ImageProcessor__heuristic(a[2], im._ImageProcessor__simplifyJSON(getJSON("uri.json"))))
        self.assertAlmostEqual(7.5, im._ImageProcessor__heuristic(a[1], im._ImageProcessor__simplifyJSON(getJSON("uri.json"))))
        self.assertAlmostEqual(4.75, im._ImageProcessor__heuristic(a[0], im._ImageProcessor__simplifyJSON(getJSON("uri.json"))))
        
    def test_db(self):
        db = serv.DBConnect()
        db.close()
        
    def test_upload(self):
        im = serv.ImageProcessor()
        file = Image.open("jrLabel.png")
        imagefile = BytesIO()
        file.save(imagefile, format='PNG')
        resp = im.uploadImage(imagefile.getvalue(), "jrLabel.png", "image/png")
        self.assertTrue("jrLabel" in resp)
        # Instantiates a client
        storage_client = storage.Client()
        bucket = storage_client.get_bucket("package-pal-images")
        blobs = bucket.list_blobs()
        a = False 
        for blob in blobs:
            if blob.name == resp:
                a = True
                blob.delete()
        self.assertTrue(a)
        file.close()
        imagefile.close()
        
    def test_process(self):
        im = serv.ImageProcessor()
        resp = str(im.processImage("jrLabel.png"))
        self.assertIn("jason", resp.lower())
        self.assertIn("warehouse", resp.lower())
        self.assertIn("locale", resp.lower())
        self.assertIn("bounding", resp.lower())
        
    def test_handle(self):
        im = serv.ImageProcessor()
        file = Image.open("jrLabel.png")
        imagefile = BytesIO()
        file.save(imagefile, format='PNG')
        resp = im.handle(imagefile.getvalue(), "jrLabel.png", "image/png")
        self.assertIn("OK", resp["status"])
        num = int(resp["id"])
        
        db = serv.PackageDB()
        entry = db.findPackage(num)
        self.assertNotIn("-1", str(entry["id"]))        
        name = entry["imageLoc"][24:]
        # Instantiates a client
        storage_client = storage.Client()
        bucket = storage_client.get_bucket("package-pal-images")
        blobs = bucket.list_blobs()
        a = False 
        for blob in blobs:
            if blob.name == name:
                a = True
        self.assertTrue(a)
        im._ImageProcessor__hardRemove(num)
        file.close()
        imagefile.close()
        
    def test_recents(self):
        db = serv.PackageDB() 
        resp = db.recents()
        self.assertEqual(5, len(resp))
        resp = db.recents(2)
        self.assertEqual(2, len(resp))
        resp = db.recents(0)["id"]
        self.assertIn("-1", str(resp))
        
    def test_findStudent(self):
        db = serv.PackageDB()
        resp = db.search("jdr145")
        found = False
        for entry in resp:
            if resp[entry]["imageLoc"][24:] == "jrLabel.png":
                found = True
        self.assertTrue(found)
        resp = db.search("adf")
        self.assertIn("-1", str(resp["id"]))
        
    def test_findPackage(self):
        db = serv.PackageDB()
        resp = db.find("9999")
        self.assertIn("-1", str(resp["id"]))
        resp = db.findPackage("14")
        self.assertIn("14", str(resp["id"]))
        self.assertIn("jdr145", resp["recipient"])
        resp = db.findPackage("-1", "jdr145", "", "Wade Commons", "gs://package-pal-images/jrLabel.png", "")
        self.assertIn("14", str(resp["id"]))
        resp = db.findPackage("-1", "jdr145", "", "Wade Commons", "", "")
        self.assertIn("14", str(resp["id"]))
        
    def test_emailToggle(self):
        resp = serv.emails(2021)
        self.assertIn("OK", str(resp["status"]))
        resp = serv.emails(2000)
        self.assertNotIn("OK", str(resp["status"]))
        
    def test_emailBuild(self):
        em = serv.EmailSend()
        resp = em.formEmail(14)
        self.assertIn("[HARLD]", str(resp.subject))
        
    def test_update(self):
        db = serv.PackageDB()
        resp = db.update(987, "jse41", "", "", "")
        self.assertIn("package", resp["status"])
        resp = db.update(14, "456", "", "", "")
        self.assertIn("invalid", resp["status"])
        string = "Village" + str(random.randint(0, 100))
        resp = db.update(18, "jse41", string, "Wade", "TestingUse")
        self.assertIn(string, resp["address"])
        

def getJSON(path):
    with open(path) as json_file:
        file = json_file.read()
    return str(file)

def getInfo():
    jacob = ["jse41", "Jacob", "Engelbrecht", "44106", "OH", "Cleveland", "House 3", "1681 E 116 St.", "133 A"]
    jason = ["jdr145", "Jason", "Richards", "44106", "OH", "Cleveland", "House 3", "1681 E 116 St.", "133 B"]
    uri = ["smk191", "Uri", "Johson", "44106", "OH", "Cleveland Heights", "Glaser House", "11900 Carlton Rd", "220 D"]
    ryan = ["mxh740", "Ryan", "Upson", "44106", "OH", "Cleveland", "Cutler House", "1616 E 115 St.", "420"]
    data = [jason, uri, jacob, ryan]
    return data 


if __name__ == '__main__':
    print("Testing has Begun")
    unittest.main()
