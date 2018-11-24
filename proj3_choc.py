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
            return None
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
    queryList = []
    commandList = command.split()
    if commandList[0].lower() == "bars":
        if len(commandList) > 1:
            print("here!")
            for x in range(1,len(commandList)-1):
                if commandList[x][1:11].lower() == "sellcountry":
                    print("sell country")
                elif commandList[x][0:13].lower() == "sourcecountry":
                    print("sourcecountry")
                elif commandList[x][0:10].lower() == "sellregion":
                    print("sellregion")
                elif commandList[x][0:12].lower() == "sourceregion":
                    print("sourceregion")


            ###sellcountry=alpha2, sourcecountry=alpha2, sellregion=name, sourceregion=name (default none)
            ###ratings | cocoa (default ratings)
            ###top=limit | bottom=limit (default = 10)
        print("bars!")
    elif commandList[0].lower() == "companies":
        print("companies!")
    elif commandList[0].lower() == "countries":
        print("countries!")
    elif commandList[0].lower() == "regions":
        print("regions!")
    else:
        print("Please enter a valid command")

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

# Make sure nothing runs or prints out when this file is run as a module
if __name__=="__main__":
    create_db()
    populate_countries(COUNTRIESJSON)
    populate_bars(BARSCSV)
    interactive_prompt()
