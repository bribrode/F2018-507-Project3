##Brianna Broderick
##SI 507 - Fall 2018
##Project 3

import sqlite3
import csv
import json

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data frxom CSV and JSON into a new database called choc.db
DBNAME = 'choc.db'
BARSCSV = 'flavors_of_cacao_cleaned.csv'
COUNTRIESJSON = 'countries.json'

###############################
###############################
##Parameter: database filename
##Wipes tables from database if they exist and (re)builds the tables
def create_db(database):
    conn = sqlite3.connect(databse)
    cur = conn.cursor()

    ##WIPE THE DB
    statement = "DROP TABLE IF EXISTS 'Bars'"
    cur.execute(statement)

    statement = "DROP TABLE IF EXISTS 'Countries'"
    cur.execute(statement)

    ##Build the Bars Table
    statement = '''
        CREATE TABLE 'Bars' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Company' TEXT,
            'SpecificBeanBarName' TEXT,
            'REF' TEXT,
            'ReviewDate' TEXT,
            'CocoaPercent' REAL,
            'CompanyLocationId' INTEGER,
            'Rating' REAL,
            'BeanType'  TEXT,
            'BroadBeanOriginId' INTEGER )
        '''
    cur.execute(statement)

    ##Build the Countries Table
    statement = '''
        CREATE TABLE 'Countries' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Alpha2' TEXT,
            'Alpha3' TEXT,
            'EnglishName' TEXT,
            'Region' TEXT,
            'Subregion' TEXT,
            'Population' INTEGER,
            'Area' REAL )
        '''
    cur.execute(statement)

    conn.commit()
    conn.close()

###############################
###############################
##Helper fxn for populating the Countries table
##Checks to see if value is in JSON Database, if it is not, returns None
##Simply to avoid writing out repeated checks, ensures that database will have Null value instead of empty string
def check_data_json(dictName, keyName):
    if not dictName[keyName]:
        return None
    else:
        return dictName[keyName]

###############################
###############################
##Reads info from Countries JSON and appropriately inserts into table
def populate_countries(country_json):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    with open(country_json) as file:
        countryInfo = json.load(file)

        for country in countryInfo:
            engName = check_data_json(country, "name")
            alpha2 = check_data_json(country, "alpha2Code")
            alpha3 = check_data_json(country, "alpha3Code")
            region = check_data_json(country, "region")
            subregion = check_data_json(country, "subregion")
            pop = check_data_json(country, "population")
            area = check_data_json(country, "area")

            vals = (None, alpha2, alpha3, engName, region, subregion, pop, area)

            statement = "INSERT INTO 'Countries' VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            cur.execute(statement, vals)

    conn.commit()
    conn.close()

###############################
###############################
##Helper fxn for clean handling of Bars csv data
##Returns value as None if not in csv
##Strips % from percentage data
##Pulls foreign keys for Countries
def check_data_csv(rowList, index):
    if not rowList[index]:
        return None
    elif index == 4:
        return rowList[index][:-1]
    elif index == 5 or index == 8:
        if rowList[index] == "Unknown":
            return None
        else:
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()

            statement = "SELECT Id FROM 'Countries' WHERE EnglishName = ?"
            val = (rowList[index],)
            cur.execute(statement, val)

            for row in cur:
                return row[0]

            conn.close()
    else:
        return rowList[index]

###############################
###############################
##Read info from country JSON and appropriately insert into table
def populate_bars(bar_csv):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    with open(bar_csv, encoding='utf-8') as file:
        csvReader = csv.reader(file)
        ##Skip headers
        next(csvReader)
        for row in csvReader:
            company = check_data_csv(row, 0)
            beanbarName = check_data_csv(row, 1)
            ref = check_data_csv(row, 2)
            reviewDate = check_data_csv(row, 3)
            cocoapercent = check_data_csv(row, 4)
            companyLocId = check_data_csv(row, 5)
            rating = check_data_csv(row, 6)
            beanType = check_data_csv(row, 7)
            broadBeanId = check_data_csv(row, 8)

            vals = (None, company, beanbarName, ref, reviewDate, cocoapercent, companyLocId, rating, beanType, broadBeanId)

            statement = "INSERT INTO 'Bars' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cur.execute(statement, vals)

    conn.commit()
    conn.close()


# Part 2: Implement logic to process user commands
###############################
###############################
##Parameter - command string entered by user
##Gracefully handles invalid commands
##appropriately handles valid commands - (bars, countries, companies, regions) and their parameters
def process_command(command):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    queryList = []
    commandList = command.split()

    if commandList:
        ##Bars Command handling
        if commandList[0] == "bars":
            possibleParams = ["sellcountry", "sourcecountry", "sellregion", "sourceregion", "top", "bottom"]
            limitSearch = False
            sortBy = "b.Rating"
            sortOrder = "desc"
            limit = 10
            countryType = ""
            placeType = ""
            placeName = ""

            if len(commandList) > 1:

                ##Check to see if all commands entered are valid
                for x in range(1,len(commandList)):
                    if commandList[x] != "ratings" and commandList[x] != "cocoa":
                        try:
                            currParams = commandList[x].split("=")
                        except:
                            print("Command Not Recognized: " + command)
                            return queryList
                        if currParams[0] in possibleParams:
                            if len(currParams) != 2:
                                print("Command Not Recognized: " + command)
                                return queryList
                        else:
                            print("Command Not Recognized: " + command)
                            return queryList

                ##Assign variables to represent each command entered
                for x in range(1,len(commandList)):
                    if commandList[x] == "ratings":
                        sortBy = "b.Rating"
                    elif commandList[x] == "cocoa":
                        sortBy = "b.CocoaPercent"
                    else:
                        currParams = commandList[x].split("=")
                        if currParams[0] == "top":
                            sortOrder = "desc"
                            limit = currParams[1]
                        elif currParams[0] == "bottom":
                            sortOrder = "asc"
                            limit = currParams[1]
                        elif currParams[0] == "sellcountry":
                            limitSearch = True
                            countryType = "sell"
                            placeType = "country"
                            placeName = currParams[1]
                        elif currParams[0] == "sourcecountry":
                            limitSearch = True
                            countryType = "source"
                            placeType = "country"
                            placeName = currParams[1]
                        elif currParams[0] == "sellregion":
                            limitSearch = True
                            countryType = "sell"
                            placeType = "region"
                            placeName = currParams[1]
                        elif currParams[0] == "sourceregion":
                            limitSearch = True
                            countryType = "source"
                            placeType = "region"
                            placeName = currParams[1]

            ##Complete Bars Query
            if limitSearch:
                statement = 'SELECT b.SpecificBeanBarName, b.Company, sell.EnglishName, b.Rating, b.CocoaPercent, source.EnglishName '
                statement += 'FROM Bars as b LEFT JOIN Countries as sell ON b.CompanyLocationId = sell.Id '
                statement += 'LEFT JOIN Countries as source ON b.BroadBeanOriginId = source.Id '
                statement += 'GROUP BY b.Id '
                statement += 'HAVING {} = "{}" '
                statement += 'ORDER BY {} {} '
                statement += 'LIMIT {} '

                if placeType == "country":
                    if countryType == "sell":
                        typeofPlace = "sell.Alpha2"
                    else:
                        typeofPlace = "source.Alpha2"
                else:
                    if countryType == "sell":
                        typeofPlace = "sell.Region"
                    else:
                        typeofPlace = "source.Region"

                cur.execute(statement.format(typeofPlace, placeName, sortBy, sortOrder, limit))

            else:
                statement = 'SELECT b.SpecificBeanBarName, b.Company, sell.EnglishName, b.Rating, b.CocoaPercent, source.EnglishName '
                statement += 'FROM Bars as b LEFT JOIN Countries as sell ON b.CompanyLocationId = sell.Id '
                statement += 'LEFT JOIN Countries as source ON b.BroadBeanOriginId = source.Id '
                statement += 'ORDER BY {} {} '
                statement += 'LIMIT {} '
                cur.execute(statement.format(sortBy, sortOrder, limit))

            for row in cur:
                queryList.append(row)

        ###Companies command handling
        elif commandList[0] == "companies":
            possibleParams = ["country", "region", "top", "bottom"]
            limit = 10
            sortOrder = "desc"
            sortBy = "AVG(Bars.Rating)"
            placeName = ""
            placeType = ""
            limitSearch = False

            if len(commandList) > 1:

                ##Check to see if all commands entered are valid
                for x in range(1,len(commandList)):
                    if commandList[x] != "ratings" and commandList[x] != "cocoa" and commandList[x] != "bars_sold":
                        try:
                            currParams = commandList[x].split("=")
                        except:
                            print("Command Not Recognized: " + command)
                            return queryList
                        if currParams[0] in possibleParams:
                            if len(currParams) != 2:
                                print("Command Not Recognized: " + command)
                                return queryList
                        else:
                            print("Command Not Recognized: " + command)
                            return queryList

                ##Assign variables representing entered commands
                for x in range(1,len(commandList)):
                    if commandList[x] == "ratings":
                        sortBy = "AVG(Bars.Rating)"
                    elif commandList[x] == "cocoa":
                        sortBy = "AVG(Bars.CocoaPercent)"
                    elif commandList[x] == "bars_sold":
                        sortBy = "COUNT(Bars.SpecificBeanBarName)"
                    else:
                        currParams = commandList[x].split("=")
                        if currParams[0] == "top":
                            sortOrder = "desc"
                            limit = currParams[1]
                        elif currParams[0] == "bottom":
                            sortOrder = "asc"
                            limit = currParams[1]
                        elif currParams[0] == "country":
                            limitSearch = True
                            placeType = "country"
                            placeName = currParams[1]
                        elif currParams[0] == "region":
                            limitSearch = True
                            placeType = "region"
                            placeName = currParams[1]

            ##Complete Company query
            if limitSearch:
                statement = 'SELECT Bars.Company, Countries.EnglishName, {} '
                statement += 'FROM Bars LEFT JOIN Countries ON Bars.CompanyLocationId = Countries.Id '
                statement += 'GROUP BY Bars.Company '
                statement += 'HAVING COUNT(Bars.SpecificBeanBarName) > 4 '
                statement += 'and {} = "{}" '
                statement += 'ORDER BY {} {} '
                statement += 'LIMIT {} '

                if placeType == "country":
                    typeofPlace = "Countries.Alpha2"
                else:
                    typeofPlace = "Countries.Region"

                cur.execute(statement.format(sortBy, typeofPlace, placeName, sortBy, sortOrder, limit))

            else:
                statement = 'SELECT Bars.Company, Countries.EnglishName, {} '
                statement += 'FROM Bars LEFT JOIN Countries ON Bars.CompanyLocationId = Countries.Id '
                statement += 'GROUP BY Bars.Company '
                statement += 'HAVING COUNT(Bars.SpecificBeanBarName) > 4 '
                statement += 'ORDER BY {} {} '
                statement += 'LIMIT {} '
                cur.execute(statement.format(sortBy, sortBy, sortOrder, limit))

            for row in cur:
                queryList.append(row)

        ##Countries Command Handling
        elif commandList[0] == "countries":
            possibleParams = ["region", "top", "bottom"]
            limit = 10
            sortOrder = "desc"
            sortBy = "AVG(Bars.Rating)"
            placeName = ""
            placeType = "Bars.CompanyLocationId = Countries.Id "
            limitSearch = False
            group = "Bars.CompanyLocationId"

            if len(commandList) > 1:

                ##Check to see if all commands entered are valid
                for x in range(1,len(commandList)):
                    if commandList[x] != "ratings" and commandList[x] != "cocoa" and commandList[x] != "bars_sold" and commandList[x] != "sellers" and commandList[x] != "sources":
                        try:
                            currParams = commandList[x].split("=")
                        except:
                            print("Command Not Recognized: " + command)
                            return queryList
                        if currParams[0] in possibleParams:
                            if len(currParams) != 2:
                                print("Command Not Recognized: " + command)
                                return queryList
                        else:
                            print("Command Not Recognized: " + command)
                            return queryList

                ##Assign variables representing entered commands
                for x in range(1,len(commandList)):
                    if commandList[x] == "ratings":
                        sortBy = "AVG(Bars.Rating)"
                    elif commandList[x] == "cocoa":
                        sortBy = "AVG(Bars.CocoaPercent)"
                    elif commandList[x] == "bars_sold":
                        sortBy = "COUNT(Bars.SpecificBeanBarName)"
                    elif commandList[x] == "sellers":
                        placeType = "Bars.CompanyLocationId = Countries.Id "
                        group = "Bars.CompanyLocationId"
                    elif commandList[x] == "sources":
                        placeType = "Bars.BroadBeanOriginId = Countries.Id"
                        group = "Bars.BroadBeanOriginId"
                    else:
                        currParams = commandList[x].split("=")
                        if currParams[0] == "top":
                            sortOrder = "desc"
                            limit = currParams[1]
                        elif currParams[0] == "bottom":
                            sortOrder = "asc"
                            limit = currParams[1]
                        elif currParams[0] == "region":
                            limitSearch = True
                            placeName = currParams[1]

            ##Complete Countries Query
            if limitSearch:
                statement = 'SELECT Countries.EnglishName, Countries.Region, {} '
                statement += 'FROM Bars LEFT JOIN Countries ON {} '
                statement += 'GROUP BY {} '
                statement += 'HAVING COUNT(Bars.SpecificBeanBarName) > 4 '
                statement += 'and Countries.Region = "{}"'
                statement += 'ORDER BY {} {} '
                statement += 'LIMIT {}'

                cur.execute(statement.format(sortBy, placeType, group, placeName, sortBy, sortOrder, limit))

            else:
                statement = 'SELECT Countries.EnglishName, Countries.Region, {} '
                statement += 'FROM Bars LEFT JOIN Countries ON {} '
                statement += 'GROUP BY {} '
                statement += 'HAVING COUNT(Bars.SpecificBeanBarName) > 4 '
                statement += 'ORDER BY {} {} '
                statement += 'LIMIT {}'

                cur.execute(statement.format(sortBy, placeType, group, sortBy, sortOrder, limit))

            for row in cur:
                queryList.append(row)

        ##Regions Command Handling
        elif commandList[0] == "regions":
            pass
            #handle regions parameters
        elif commandList[0] == "exit":
            return queryList
        else:
            print("Command Not Recognized: " + command)
            return queryList
    else:
        return queryList


    for item in queryList:
        print(item)

    conn.close()
    return queryList


def load_help_text():
    with open('help.txt') as f:
        return f.read()

# Part 3: Implement interactive prompt. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('\nEnter a command: ')

        if response == 'help':
            print(help_text)
            continue
        else:
            process_command(response)

    print("Goodbye!")

# Make sure nothing runs or prints out when this file is run as a module
if __name__=="__main__":
    create_db(DBNAME)
    populate_countries(COUNTRIESJSON)
    populate_bars(BARSCSV)
    interactive_prompt()
