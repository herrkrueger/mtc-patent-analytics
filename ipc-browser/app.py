from flask import Flask, render_template, request, jsonify, make_response
import sqlite3
import pandas as pd
from TreeData import TreeData
import json

DB_NAME = 'patent-classification.db'

app = Flask(__name__)

@app.route("/")
def default():
    return render_template('tree.html', scheme="IPC", language="en")

@app.route("/CPC/en")
def cpc_en():
    return render_template('tree.html', scheme="CPC", language="en")

@app.route("/IPC/en")
def ipc_en():
    return render_template('tree.html', scheme="IPC", language="en")

@app.route("/IPC/fr")
def ipc_fr():
    return render_template('tree.html', scheme="IPC", language="fr")

# when page is loaded, get scheme then return first level of tree
@app.route('/root', methods=['GET','POST'])
def root():
    data = request.get_json()
    scheme = data['scheme'] 
    if scheme == 'CPC':
        children = cpc_tree_data.get_children(1, scheme, cpc_by_level_and_parent)
    elif scheme == 'IPC':
        children = ipc_tree_data.get_children(1, scheme, ipc_by_level_and_parent)
    root = {"name": scheme, "children": children}
    return jsonify(root)
  

# after click on node, get scheme, symbol, level then return direct children from database
@app.route('/children', methods=['GET','POST'])
def children():
    data = request.get_json()
    scheme = data['scheme']
    symbol = data['name'].split('-')[0]
    level = int(data['depth']) + 1
    if scheme == 'CPC':
        children = cpc_tree_data.get_children(level, symbol, cpc_by_level_and_parent)
    elif scheme == 'IPC':
        children = ipc_tree_data.get_children(level, symbol, ipc_by_level_and_parent)
    return jsonify(children)

# after click on node, get scheme, language, current tree then update titles table
@app.route('/titles', methods = ['GET','POST'])
def titles():
    data = request.get_json()
    scheme = data['scheme'] 
    language = data['language']
    tree = data['json_tree']
    if scheme == 'CPC':
        symbols = cpc_tree_data.flatten_nested_json(json.loads(tree))
        titles = cpc_tree_data.get_titles(symbols)
    elif scheme == 'IPC':
        symbols = ipc_tree_data.flatten_nested_json(json.loads(tree))
        titles = ipc_tree_data.get_titles(language, symbols)
    return jsonify(titles)  

if __name__ == '__main__':

    # connect to database
    conn = sqlite3.connect('./' + DB_NAME)

    # read table from database and group by level and parent to ease access to children
    # initiate TreeData class (to process data)

    ipc = pd.read_sql_query("SELECT * FROM ipc", conn)
    ipc_by_level_and_parent = ipc.groupby(['level', 'parent'])
    ipc_tree_data = TreeData(ipc, ipc_by_level_and_parent)

    #cpc = pd.read_sql_query("SELECT * FROM cpc", conn)
    #cpc_by_level_and_parent = cpc.groupby(['level', 'parent'])
    #cpc_tree_data = TreeData(cpc, cpc_by_level_and_parent)

    # run app
    app.run(debug=True, host="0.0.0.0") 
