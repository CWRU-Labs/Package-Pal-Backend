# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 20:42:11 2019

@author: jacob
"""

import unittest 

class TestStringMethods(unittest.TestCase):

    def test_findUser(self):
        self.assertEqual(findUser(getJSON("data.json")), 'jse41')
        self.assertEqual(findUser(getJSON("uri.json")), 'smk191')
        
    def test_simplifyJSON(self):
        self.assertTrue("locale" not in simplifyJSON(getJSON("data.json")))
        self.assertTrue("bounding" not in simplifyJSON(getJSON("data.json")))
        
"""
    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)"""

def getInfo():
    """    
    ids = ["jse41", "jdr145", "smk191", "mxh740"]
    firstNames = ["Jacob", "Jason", "Uri", "Ryan"]
    lastNames = ["Engelbrecht", "Richards", "Johson", "Upsol"]
    zips = ["44106", "44106", "44106", "44106"]
    state = ["OH", "OH", "OH", "OH"]
    city = ["Cleveland", "Cleveland", "Cleveland Heights", "Cleveland"]
    house = ["House 3", "House 3", "Glaser House", "Curlet House"]
    address = ["1681 E 116 St.", "1681 E 116 St.", "11900 Carlton Rd", "1616 E 115 St."]
    room = ["133 A", "133 B", "220 D", "420"]
    """
    jacob = ["jse41", "Jacob", "Engelbrecht", "44106", "OH", "Cleveland", "House 3", "1681 E 116 St.", "133 A"]
    jason = ["jdr145", "Jason", "Richards", "44106", "OH", "Cleveland", "House 3", "1681 E 116 St.", "133 B"]
    uri = ["smk191", "Uri", "Johson", "44106", "OH", "Cleveland Heights", "Glaser House", "11900 Carlton Rd", "220 D"]
    ryan = ["mxh740", "Ryan", "Upson", "44106", "OH", "Cleveland", "Cutler House", "1616 E 115 St.", "420"]
    data = [jason, uri, jacob, ryan]
    return data 
    

def getJSON(path):
    with open(path) as json_file:
        file = json_file.read()
    return file

def simplifyJSON(json):
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

def findUser(json):
    data = getInfo()
    ranks = []
    for person in data:
        ranks.append(heuristic(person, simplifyJSON(json)))
    maxVal = [0, 0]
    for i in range(0, len(ranks)):
        if ranks[i] > maxVal[0]:
            maxVal[0] = ranks[i]
            maxVal[1] = i
    return data[maxVal[1]][0]
    

def heuristic(person, data): 
    value = 0
    for index in range (1, len(person)):
        for word in person[index].split(" "):
            if word in data:
                value += 1 / len(person[index].split(" "))
    return value

if __name__ == '__main__':
    print("Testing has Begun")
    unittest.main()