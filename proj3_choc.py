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

##Wipes tables from database if they exist and (re)builds the tables
def create_db():
    conn = sqlite3.connect(DBNAME)
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

##Checks to see if value is in JSON Database, if it is not, returns NULL
##Simply to avoid writing out repeated checks
def check_data_json(dictName, keyName):
    if not dictName[keyName]:
        return None
    else:
        return dictName[keyName]

##Read info from country JSON and appropriately insert into table
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

            statement = 'INSERT INTO "Countries" VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
            cur.execute(statement, vals)

    conn.commit()
    conn.close()


##Clean handling of csv data
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
            return "Unknown"
        else:
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()

            statement = 'SELECT Id FROM "Countries" WHERE EnglishName = ?'
            val = (rowList[index],)
            cur.execute(statement, val)

            for row in cur:
                return row[0]

            conn.close()
    else:
        return rowList[index]



##Read info from country JSON and appropriately insert into table
def populate_bars(bar_csv):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    with open(bar_csv) as file:
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

            statement = 'INSERT INTO "Bars" VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            cur.execute(statement, vals)

    conn.commit()
    conn.close()



# Part 2: Implement logic to process user commands
def process_command(command):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    queryList = []
    possibleParams = ["sellcountry", "sourcecountry", "sellregion", "sourceregion", "top", "bottom"]
    commandList = command.split()
    limitSearch = False
    sortBy = "b.Rating"
    sortOrder = "desc"
    limit = 10
    countryType = ""
    placeType = ""
    placeName = ""


    if commandList:
        if commandList[0] == "bars":
            if len(commandList) > 1:
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

            ###query the database


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

                print(typeofPlace + " " + placeName + " " + sortBy + " " + sortOrder + " " + str(limit))
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

            #handle bars parameters
        elif commandList[0] == "companies":
            pass
            #handle companies parameters
            ##Company, company location, requested aggregation
        elif commandList[0] == "countries":
            pass
            #handle countries parameters
        elif commandList[0] == "regions":
            pass
            #handle regions parameters
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
        response = input('Enter a command: ')

        if response == 'help':
            print(help_text)
            continue
        else:
            process_command(response)

    print("Goodbye!")

# Make sure nothing runs or prints out when this file is run as a module
if __name__=="__main__":
    create_db()
    populate_countries(COUNTRIESJSON)
    populate_bars(BARSCSV)
    interactive_prompt()
