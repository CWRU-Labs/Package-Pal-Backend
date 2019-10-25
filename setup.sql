CREATE DATABASE packagePal;

use packagePal; 

CREATE TABLE Housing(
	housingID int NOT NULL Primary Key AUTO_INCREMENT, 
	address varchar(255) NOT NULL,
	city varchar(63), 
	st char(2), 
	zip int,
	name varchar(127),
	room varchar(63) NOT NULL
);

CREATE TABLE Student(
	studentID varchar(7) NOT NULL Primary Key, 
	firstName varchar(63) NOT NULL, 
	lastName varchar(63) NOT NULL, 
	house int,
	FOREIGN KEY (house) REFERENCES Housing(housingID)
);

CREATE TABLE Package(
	packageID int NOT NULL Primary Key AUTO_INCREMENT, 
	recipient varchar(7) NOT NULL, 
	address varchar(255) NOT NULL,
	location varchar(127) NOT NULL, 
	dateTimeIn datetime NOT NULL, 
	dateTimeOut datetime, 
	completeText varchar(2047), 
	imageLoc varchar(63), 
	description varchar(511), 
	FOREIGN KEY (recipient) REFERENCES Student(studentID)
);

INSERT INTO Housing(housingID, address, city, st, zip, name, room) 
	VALUES (2, "1681 E 116 St.", "Cleveland", "OH", 44106, "House 3", "133 A");
INSERT INTO Student(studentID, firstName, lastName, house) VALUES ("jse41", "Jacob", "Engelbrecht", 2);

INSERT INTO Housing(housingID, address, city, st, zip, name, room) 
	VALUES (3, "1616 E 115 St.", "Cleveland", "OH", 44106, "Cutler House", "420");
INSERT INTO Student(studentID, firstName, lastName, house) VALUES ("mxh740", "Ryan", "Upsol", 3);

INSERT INTO Housing(housingID, address, city, st, zip, name, room) 
	VALUES (4, "11900 Carlton Rd", "Cleveland Heights", "OH", 44106, "Glaser House", "220 D");
INSERT INTO Student(studentID, firstName, lastName, house) VALUES ("smk191", "Uri", "Johson", 4);

INSERT INTO Housing(housingID, address, city, st, zip, name, room) 
	VALUES (5, "1681 E 116 St.", "Cleveland", "OH", 44106, "House 3", "133 B");
INSERT INTO Student(studentID, firstName, lastName, house) VALUES ("jdr145", "Jason", "Richards", 5);