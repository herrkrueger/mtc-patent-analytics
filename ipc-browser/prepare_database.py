# connet and querying database
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.url import URL
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.types import String
import sqlite3
# process data
import pandas as pd
from lxml import etree as ET
from sklearn import preprocessing
import re
import time
import json
# to open the xml files
import requests, zipfile, io, os
import tempfile
from io import StringIO
# config and db class
from config import config
from database import database

if __name__ == '__main__':

    # initiate configuration class
    config = config()
    reqsD = config.connect_to_database()
    fileD = config.files()

    # connect to database
    engine = create_engine(str(URL(**reqsD))+ '/patent_classification')
    if database_exists(engine.url) == False:
       create_database(engine.url)
       conn = engine.connect()
       conn.execute('CREATE SCHEMA patent_classification')
    else:
        conn = engine.connect()

    inspector = inspect(engine)
    scheme = input('Choose between cpc or ipc: ').lower()
    if scheme in inspector.get_table_names():
        conn.execute('DROP TABLE patent_classification.' + scheme)
    
    database = database()

    # df with symbols, kinds and direct parents..
    #database.importer(scheme, fileD, schemaL, engine, conn)

    # ..add column for levels
    #database.add_levels(scheme, engine)

    # ..add column for short symbols
    #database.add_symbols_short(scheme, engine)

    if scheme == 'ipc':
        schemeD = {'en' : fileD['ipc_en'], 'fr': fileD['ipc_fr']}
        index = 'symbol'
    elif scheme == 'cpc':
        schemeD = {'en' : fileD['cpc_en']}
        index = 'symbol_short'

    # ..add columns for titles
    #database.get_titles(scheme, schemeD, index, engine)

    # ..add columns for creation_dates
    #database.pc_evolution(scheme, index, engine, fileD)

    # ..add columns for sizes i.e. number of groups contained (in % and normalised)
    database.get_paths(scheme, engine)
    #database.pc_statistics(scheme, engine)

    # from postgresql to sqlite
    #database.postgresql_to_sqlite(scheme, engine)
