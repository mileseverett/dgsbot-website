import mysql.connector
import os
from dotenv import load_dotenv


def makeConn():
    load_dotenv(verbose=True)
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    host = os.getenv('MYSQL_HOST')
    port = os.getenv('MYSQL_PORT')

    conn = mysql.connector.connect(user=user
                            ,password=password
                            ,host=host
                            ,port=port
                            ,database='DGS_Hiscores'
                            ,use_pure=True)
    return conn

def uploadToDB( playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime, imageLink, secretValue):
    # Connect to DB
    conn = makeConn()

    query_string = "INSERT INTO submission_raw (playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime, imageLink) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime, imageLink)
    try:
        cursor = conn.cursor()
        cursor.execute(query_string)
        floorID = cursor.lastrowid
        cursor.close()
        
        cursor = conn.cursor()
        print ("INSERT INTO submission_status (floorID, userCompletedInd, adminReviewInd, websiteLink, submitterID) values ({}, 0, 0, '{}', 12)".format(floorID,secretValue))
        cursor.execute("INSERT INTO submission_status (floorID, userCompletedInd, adminReviewInd, websiteLink, submitterID) values ({}, 0, 0, '{}', 12)".format(floorID,secretValue))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return True, floorID

def retrieveFloorStatus(floorID):
    #connect to DB
    conn = makeConn()

    query_string = "SELECT * FROM submission_status WHERE floorID = {};".format(int(floorID))
    try:
        cursor = conn.cursor()
        cursor.execute(query_string)
        data = cursor.fetchall()
        cursor.close()
        conn.commit()
    finally:
        conn.close()
        return data

def retrieveFloorRaw(floorID):
    #connect to DB
    conn = makeConn()
    query_string = "SELECT * FROM submission_raw WHERE floorID = {};".format(int(floorID))
    try:
        cursor = conn.cursor()
        cursor.execute(query_string)
        data = cursor.fetchall()
        cursor.close()
        conn.commit()
    finally:
        conn.close()
        return data

def retrieveCompleted():
    #connect to DB
    conn = makeConn()
    query_string = "SELECT * FROM reviewFloors"
    try:
        cursor = conn.cursor()
        cursor.execute(query_string)
        data = cursor.fetchall()
        cursor.close()
        conn.commit()
    finally:
        conn.close()
        return data

def updateSubmissionStatus(floorID, completedInd):
    conn = makeConn()

    query_string = "UPDATE submission_status set userCompletedInd = 1 WHERE floorID = {};".format(int(floorID))
    try:
        cursor = conn.cursor()
        cursor.execute(query_string)
        conn.commit()
    finally:
        if (conn.is_connected()):
            conn.close()
            print("MySQL connection is closed") 

def updateFloor(floorID,playerOne,playerTwo,playerThree,playerFour,playerFive,endTime,theme):
    conn = makeConn()
    query_string = "UPDATE submission_raw set playerOne = '{}', playerTwo = '{}', playerThree = '{}', playerFour = '{}', playerFive = '{}', theme = '{}', endTime = '{}' WHERE floorID = {};".format(str(playerOne),str(playerTwo),str(playerThree),str(playerFour),str(playerFive),str(theme),str(endTime),int(floorID))
    try:
        cursor = conn.cursor()
        cursor.execute(query_string)
        conn.commit()
    finally:
        if (conn.is_connected()):
            conn.close()
            print("MySQL connection is closed") 