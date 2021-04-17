import mysql.connector
import os
from dotenv import load_dotenv


def makeConn():
    load_dotenv(verbose=True)
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    host = os.getenv('MYSQL_HOST')
    port = os.getenv('MYSQL_PORT')
    print (user,password,host,port)
    conn = mysql.connector.connect(user=user
                            ,password=password
                            ,host=host
                            ,port=port
                            ,database='DGS_Hiscores'
                            ,use_pure=True)
    return conn

def uploadToDB(playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime, imageLink, secretValue):
    # Connect to DB
    conn = makeConn()

    query_string = "INSERT INTO submission_raw (playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime, imageLink) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime, imageLink)
    try:
        cursor = conn.cursor()
        cursor.execute(query_string)
        floorID = cursor.lastrowid
        cursor.close()
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO submission_status (floorID, userCompletedInd, adminReviewInd, websiteLink, submitterID) values ({}, 0, 0, '{}', 12)".format(floorID,secretValue))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return True, floorID

def uploadToAcceptedDB(floorID, playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime, imageLink, submitterID):
    # Connect to DB
    conn = makeConn()
    query_string = "INSERT INTO submission_accepted (floorID, playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime, imageLink, submitterID) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}','{}')".format(floorID, playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime, imageLink, submitterID)
    print (query_string)
    try:
        cursor = conn.cursor()
        cursor.execute(query_string)
        cursor.close()
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

def retrieveAdminPageRaw(adminID):
    #connect to DB
    conn = makeConn()
    query_string = "SELECT * FROM admin_links WHERE sessionID = {};".format(int(adminID))
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

def updateAdminStatus(floorID):
    conn = makeConn()

    query_string = "UPDATE submission_status set adminReviewInd = 1 WHERE floorID = {};".format(int(floorID))
    try:
        cursor = conn.cursor()
        cursor.execute(query_string)
        conn.commit()
    finally:
        if (conn.is_connected()):
            conn.close()
            print("MySQL connection is closed") 

def updateFloor(floorID, playerOne, playerTwo, playerThree, playerFour, playerFive, endTime, theme):
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

def grabTopNAppearances(n = 10, tableType = "overall"):
    conn = makeConn()
    cursor = conn.cursor()
    if tableType == "overall":
        query_string = "select player, appearances from playerAppearances order by appearances desc"
    elif tableType == "monthly":
        query_string = "select player, appearances from monthlyAppearances order by appearances desc"
    else:
        raise("Unknown table type")

    cursor.execute(query_string)
    topn = cursor.fetchmany(n)
    return topn

def grabTopNByTheme(theme, n = 10, tableType = "overall"):
    conn = makeConn()
    cursor = conn.cursor()
    if tableType == "overall":
        query_string = "select * from DGS_Hiscores.submission_accepted where theme = '{}' order by endTime, acceptedTimestamp".format(str(theme))
    elif tableType == "monthly":
        query_string = "select * from DGS_Hiscores.monthlyFloors where theme = '{}' order by endTime, acceptedTimestamp".format(str(theme))
    else:
        raise("Unknown table type")

    cursor.execute(query_string)
    topn = cursor.fetchmany(n)
    
    # change dates
    topn = [list(x) for x in topn]

    for index, item in enumerate(topn):
        item[7] = str(item[7])[3:]
        item[9] = item[9].date().strftime('%b %d, %Y')
        item.insert(11, index + 1)

    return topn

def grabTopNOverall(n = 10, tableType = "overall"):
    conn = makeConn()
    cursor = conn.cursor()
    if tableType == "overall":
        query_string = "select * from DGS_Hiscores.submission_accepted order by endTime, acceptedTimestamp"
    elif tableType == "monthly":
        query_string = "select * from DGS_Hiscores.monthlyFloors order by endTime, acceptedTimestamp"
    else:
        raise("Unknown table type")

    cursor.execute(query_string)
    topn = cursor.fetchmany(n)

    # change dates
    topn = [list(x) for x in topn]

    for index, item in enumerate(topn):
        item[7] = str(item[7])[3:]
        item[9] = item[9].date().strftime('%b %d, %Y')
        item.insert(11, index + 1)

    return topn