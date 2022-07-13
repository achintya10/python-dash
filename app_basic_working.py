import dash
from dash.dependencies import Input, Output, State
from dash import Dash, dash_table, dcc, html, ctx
#import dash_core_components as dcc
#import dash_html_components as html
#import mysql.connector
from sqlalchemy import create_engine
import pymysql

import pandas as pd
import plotly.express as px

#try:
    #cnx = mysql.connector.connect(user='root', password='', host='127.0.0.1',  database='online_movie_rating', use_pure=False)
sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/online_movie_rating')
dbConnection    = sqlEngine.connect()
#cursor = dbConnection.cursor()
#cursor.execute('select title, release_year, genre,collection_in_mil from movies2');
df_rows = pd.read_sql("select title, release_year, genre,collection_in_mil from movies2", dbConnection);
#rows = cursor.fetchall()
#print(df_rows)
no_of_rows = df_rows.shape[0]
dbConnection.close()
#print(no_of_rows)
#except mysql.connector.Error as err:
 # if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
 #   print("Something is wrong with your user name or password")
 # elif err.errno == errorcode.ER_BAD_DB_ERROR:
 #   print("Database does not exist")
 # else:
#    print(err)
#else:
  #cnx.close()
  

app = dash.Dash(__name__)

app.layout = html.Div([
    dash_table.DataTable(
        id='our-table',
        columns=[{'name': 'Title', 'id': 'title', 'deletable': False, 'renamable': False},
                 {'name': 'Release', 'id': 'release_year', 'deletable': True, 'renamable': True},
                 {'name': 'Genre', 'id': 'genre', 'deletable': True, 'renamable': True},
                 {'name': 'Collection(In Miilion)', 'id': 'collection_in_mil', 'deletable': False, 'renamable': False}],
        data=[{'title': df_rows['title'][i] ,'release_year': df_rows['release_year'][i],'genre': df_rows['genre'][i],'collection_in_mil': df_rows['collection_in_mil'][i]}
            for i in range(no_of_rows)],
        editable=True,                  # allow user to edit data inside table
        row_deletable=False,             # allow user to delete rows
        sort_action="native",           # give user capability to sort columns
        sort_mode="single",             # sort across 'multi' or 'single' columns
        page_action='none',             # render all of the data at once. No paging.
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '150px', 'maxWidth': '150px'},
        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'width': '50px'
            } for c in ['Release','Genre', 'Collection']
        ]
    ),

    html.Button('Add Row', id='editing-rows-button', n_clicks=0),
    html.Button('Dumy Button', id='dummy-button', n_clicks=0, hidden=True),
    html.Button('Update', id='save_to_csv', n_clicks=0),

    # Create notification when saving to database
    html.Div(id='placeholder', children=[]),
    dcc.Store(id="store", data=0),
    dcc.Interval(id='interval', interval=1000),

    #dcc.Graph(id='my_graph')

])
# ------------------------------------------------------------------------------------------------

#@app.callback(Output('our-table', 'children'), Input('Title', 'active_cell'))
#def update_graphs(active_cell):
#    return str(active_cell) if active_cell else "Click the table"
#@app.callback(Output('our-table', 'data'),
#              [Input('fileInput', 'value')])
#def fileListUpdate(fileInput):
#    return fileInput

    
@app.callback(
    Output('our-table', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('our-table', 'data'),
     State('our-table', 'columns')],
)
def add_row(n_clicks, rows, columns):
    # print(rows)
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    # print(rows)
    return rows

@app.callback(
    [Output('placeholder', 'children'),
     Output("store", "data")],
    [Input('save_to_csv', 'n_clicks'),
     Input("interval", "n_intervals")],
    [State('our-table', 'data'),
     State('store', 'data')]
)
def df_to_csv(n_clicks, n_intervals, dataset, s):
    output = html.Plaintext("The data has been saved to your database.",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})

    #input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    input_triggered = ctx.triggered_id
    #print(input_triggered)

    if input_triggered == "save_to_csv":
        s = 3
        df = pd.DataFrame(dataset)
        tableName = 'movies2'
        #df.to_csv("Your_Sales_Data.csv")
        #df.to_sql(name='movies', con=dbConnection, if_exists = 'replace', index=False)
        try:
            sqlEngine       = create_engine('mysql+pymysql://root:@127.0.0.1/online_movie_rating')
            dbConnection1    = sqlEngine.connect()
            frame = df.to_sql(tableName, dbConnection1, if_exists='replace', index = True);
        except ValueError as vx:
            print(vx)
        except Exception as ex:   
            print(ex)
        else:
            print("Table %s updated successfully."%tableName);   
        finally:
            #print("Table %s updated successfully."%tableName);
            dbConnection1.close()
        return output, s
    elif input_triggered == 'interval' and s > 0:
        s = s-1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s


if __name__ == '__main__':
    app.run_server(debug=True)