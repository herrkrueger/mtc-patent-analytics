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

class database():

    def importer(self, scheme, fileD, schemaL, engine, conn):
        start = time.time()
        with tempfile.TemporaryDirectory() as directory:

            # unzip...
            url = fileD[scheme]
            r = requests.get(url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(directory)
            filename = os.listdir(directory)[0] #en and fr version available, for the hierarchy struture only need one 

            # ...and parse file
            parser = ET.XMLParser(remove_blank_text=True)
            path = os.path.join(directory, filename)
            tree = ET.parse(path, parser=parser)
            root = tree.getroot()

            # list of parent entries to iterate over
            parentL=[root]

            for parent in parentL:
                # create dataframe for each level and parent
                df = pd.DataFrame(columns=['kind', 'parent'])

                # iterate over children entries
                for entry in parent.iterchildren(tag='{http://www.wipo.int/classifications/ipc/masterfiles}ipcEntry'):

                    # add children to list of parents  
                    parentL.append(entry)

                    # save classification symbol
                    symbol = entry.attrib['symbol']
                    
                    # get classification level 
                    kind = entry.attrib['kind']
                    
                    # save kind and symbol of direct parent
                    if kind == "s":
                        # for entries of level 1 save "IPC" as parent
                        df.loc[symbol, 'kind']= kind
                        df.loc[symbol, 'parent']= scheme.upper()
                    elif kind not in ['t', 'i', 'g', 'n']:
                        # save only relevant entries 
                        if parent.tag == '{http://www.wipo.int/classifications/ipc/masterfiles}ipcEntry':
                            df.loc[symbol, 'kind']= kind
                            df.loc[symbol, 'parent']= parent.attrib['symbol']
                
                            
                # write to database
                df.to_sql(scheme, engine, if_exists='append', schema='patent_classification', index=True, index_label="symbol")
        print( 'importer done -- ', time.time() - start)                 

    def add_levels(self, scheme, engine):
        start = time.time()
        # save "levels" by mapping corresponding "kinds"
        df = pd.read_sql_table(scheme, engine, schema='patent_classification', index_col='symbol')
        df['level'] = df['kind']
        kind_to_levelD = {'s': 2, 'c': 3, 'u': 4, 'm' :5, '1': 6, '2': 7, '3': 8, '4': 9, '5': 10,
                        '6': 11, '7': 12, '8': 13, '9': 14, 'A': 15, 'B': 16, 'C':17} 
        df.replace({"level": kind_to_levelD}, inplace=True)
        df.to_sql(scheme, engine, if_exists='replace', schema='patent_classification', index=True)
        print( 'add_levels done -- ', time.time() - start)


    # transforms H01F0001053000 to H01F1/053
    def formatting_symbols(self, x):
        # for section, class, subclass return symbol
        if len(x)<= 4:
            return x
        else:
            # for group remove leading and trailing zeros
            x = x[:4] + str(int(x[4:8])) + '/' + x[8:].rstrip('0')
            
            if x[-1] == '/':
                return x + '00'
            else:
                return x

    def add_symbols_short(self, scheme, engine):
        start = time.time()
        df = pd.read_sql_table(scheme, engine, schema='patent_classification', index_col='symbol')
        df['symbol_short'] = list(map(lambda x: self.formatting_symbols(x), df.index.tolist()))
        df['parent_short'] = df['parent'].apply(lambda x: self.formatting_symbols(x))

        df.to_sql(scheme, engine, if_exists='replace', schema='patent_classification', index=True)
        print( 'add_symbols_short done -- ', time.time() - start)


    def get_titles(self, scheme, schemeD, index, engine):
        start = time.time()
        for language in list(schemeD.keys()):
            
            # concatenate txt files to dataframe of titles 
            titles= []
        
            # ...for the cpc it's a txt file that we have to unzip first
            if scheme == 'cpc':
                with tempfile.TemporaryDirectory() as directory:
                    r = requests.get(schemeD[language])
                    z = zipfile.ZipFile(io.BytesIO(r.content))
                    z.extractall(directory)
                    filenameL = [file for file in os.listdir(directory) if file.endswith('.txt')]
                    for filename in filenameL:
                        path = os.path.join(directory, filename)
                        df = pd.read_csv(path,  sep='\t', header=None, names=[index, 'title_' + language])
                        titles.append(df)
            else:
                for filename in schemeD[language]:
                    r = requests.get(filename)
                    byte = r.content
                    s=str(byte,'utf-8')
                    data = StringIO(s) 
                    df = pd.read_csv(data,  sep='\t', header=None, names=[index, 'title_' + language])
                    titles.append(df)
            df_titles = pd.concat(titles, axis=0, ignore_index=True)
            df_titles.drop_duplicates(subset=index, keep='last', inplace=True)

            # append titles to database
            df = pd.read_sql_table(scheme, engine, schema='patent_classification', index_col=index)
            df = df.join(df_titles.set_index(index))
            df.to_sql(scheme, engine, if_exists='replace', schema='patent_classification', index=True)
        print( 'get_titles done -- ', time.time() - start)

    def pc_evolution(self, scheme, index, engine, fileD):
        start = time.time()
        # read table from database
        df = pd.read_sql_table(scheme, engine, schema='patent_classification', index_col=index)

        # read inventory of IPC/CPC ever used symbols with creation date
        inventory = fileD[ scheme + '_inventory']
        
        # ...for the cpc it's a txt file that we have to unzip first
        if scheme == 'cpc':
            with tempfile.TemporaryDirectory() as directory:
                r = requests.get(inventory)
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall(directory)
                filename = [file for file in os.listdir(directory) if file.endswith('.txt')][0]
                path = os.path.join(directory, filename)
                
                pc_inventory = pd.read_csv(path, sep='\t', names= [index, 'creation_date', 'expiration_date'], usecols=[0,1])
        
        # ...for the ipc we can read it directly
        else:
            r = requests.get(inventory)
            byte = r.content
            s=str(byte,'utf-8')
            data = StringIO(s) 
            pc_inventory = pd.read_csv(data, sep=';', names= [index, 'creation_date', 'expiration_date'], usecols=[0,1])
        
        # we join the tables...
        df = df.join(pc_inventory.set_index(index))
        
        # ...and fill the creation dates of the section and class symbols
        if scheme == 'cpc':
            creation_data = '2013-01-01'
        else:
            creation_data = 19680901
        df.fillna(value= {'creation_date': creation_data}, inplace=True)
        
        df.to_sql(scheme, engine, if_exists='replace', schema='patent_classification', index=True, dtype={'creation_date':String()})
        print( 'pc_evolution done -- ', time.time() - start)


    # returns a list with the paths of all symbols from main groups and subgroups as lists of symbols
    def get_paths(self, scheme, engine):
        
        df = pd.read_sql_table(scheme, engine, schema='patent_classification')
        grouped_level = df.groupby('level')
        
        pathsL = []
        
        # iterte df over rows
        for index, row in df.iterrows():
            key = row['symbol']
            level = int(row['level'])
            
            # select only symbols of main groups and subgroups
            if level >4:
                path=[key]
                # trace path by appending successively the corresponding direct parent to a list
                for i in range(level , 2, -1):
                    group = grouped_level.get_group(i)
                    try:
                        parent = group[group['symbol'] == key]['parent'].iloc[0]
                        key = parent
                        path.append(parent)
                    except:
                        print(key)
                        pass
                path = path[::-1]
                pathsL.append(path)
        paths_df = pd.DataFrame(pathsL)
        paths_df.to_csv(scheme + '_statistics.csv')

    def pc_statistics(self, scheme, engine):
        start = time.time()
        # convert list of paths to dataframe and fill paths with 0 to reach maximal lenght
        paths_df = pd.read_csv(scheme + '_statistics.csv', index_col=0)
        paths_df.fillna('0', inplace=True)

        stat=[]
        # iterate df over columns in order to group by each level
        for i in range(paths_df.shape[1]):
            grouped = paths_df.groupby([str(j) for j in range(i+1)])
            
            # save symbol and it's size to list
            for key in grouped.groups.keys():
                if '0' not in key:
                    stat.append([key[-1], len(grouped.get_group(key))])

        # convert to df with the symbols and for each symbol a value corresponding to the number of groups it contains
        stat_df = pd.DataFrame(stat, columns=['symbol', 'size'])
        
        # add size in % 
        stat_df['size_percent'] = round(stat_df['size'] * 100 / 74503, 3)
        
        # append statistics to database
        df = pd.read_sql_table(scheme, engine, schema='patent_classification')
        #pathsL = get_paths(df, engine)
        df = df.set_index('symbol').join(stat_df.set_index('symbol'))
        
        # add normalised size for each group of children for visualization
        df['size_normalised'] = df['size']
        grouped = df.groupby('parent')
        for key in grouped.groups.keys():
            group = grouped.get_group(key)
            x = group['size_normalised'].values.reshape(-1, 1)
            min_max_scaler = preprocessing.MinMaxScaler(feature_range=(3, 13))
            x_scaled = min_max_scaler.fit_transform(x)
            index = group.index.values
            df.loc[index, 'size_normalised'] = x_scaled
  
        
        df.to_sql(scheme, engine, if_exists='replace', schema='patent_classification')
        print( 'pc_statistics done -- ', time.time() - start)

    def postgresql_to_sqlite(self, scheme, engine):
        df = pd.read_sql_table(scheme, engine, schema='patent_classification')
        conn2 = sqlite3.connect('./patent-classification.db')
        df.to_sql(name=scheme, schema='patent-classification', index=False, con=conn2, if_exists='replace')