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
def check_data(dictName, keyName):
    if not dictName[keyName]:
        return None
    else:
        return dictName[keyName]

##Read info from country JSON and appropriately insert into table
def populate_countries(country_json):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    file = open(country_json)
    countryInfo = json.load(file)

    for country in countryInfo:
        engName = check_data(country, "name")
        alpha2 = check_data(country, "alpha2Code")
        alpha3 = check_data(country, "alpha3Code")
        region = check_data(country, "region")
        subregion = check_data(country, "subregion")
        pop = check_data(country, "population")
        area = check_data(country, "area")

        vals = (None, alpha2, alpha3, engName, region, subregion, pop, area)

        statement = 'INSERT INTO "Countries" VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, vals)

    conn.commit()
    conn.close()


##Read info from country JSON and appropriately insert into table
def populate_bars(bar_csv):
    pass


# Part 2: Implement logic to process user commands
def process_command(command):
    return []


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

# Make sure nothing runs or prints out when this file is run as a module
if __name__=="__main__":
    create_db()
    populate_countries(COUNTRIESJSON)
    # interactive_prompt()
