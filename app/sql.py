# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 09:49:14 2023

@author: ONS2172
"""

import pyodbc 
import pandas as pd
import datetime

def get_sql_connection():

    conn = pyodbc.connect(
        # 'Driver={SQL Server};'
        'Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.0.so.1.1};'
        'Server=mdzusvpcwapp200.krft.net;'
        'Database=Reporting_Global_DW;'
        'UID=S-CAT_Reporting;'
        'PWD=password1234;'
    )
    cursor = conn.cursor()
    cursor.fast_executemany = True
    return conn, cursor

def close_sql_connection(conn):
    conn.close()
    
def genetate_query(df, table_name):
    col = len(df.columns)
    qm=""
    for i in range(col):
        qm = qm + "?, "
    qm = qm[:-2]
    
    dtlist = ['varchar', 'varchar', 'varchar', 'varchar', 'bigint', 'bigint', 'bigint', 'bigint', 'bigint', 'bigint', 'bigint', 'bigint', 'bigint', 'bigint', 'bigint', 'bigint', 'bigint', 'varchar', 'varchar']
    
    for i, col in enumerate(df.columns):
        if dtlist[i] == 'varchar' or dtlist[i] == 'date' :
            print(col)
            df[col] = df[col].fillna('')
            df[col] = df[col].astype(object)
        elif dtlist[i] == 'decimal':
            print(col)
            df[col] = df[col].astype(float)
            df[col] = df[col].round(decimals = 5)
            df[col] = df[col].fillna(0)
    
    print(df.dtypes.value_counts())

    val = list(df.itertuples(index=False, name=None))
    sql_query = "INSERT INTO " + table_name + " VALUES " + "(" + qm + ")"
    return sql_query, val
    
def execute_query(conn, cursor, sql_query, val):
    today = datetime.datetime.now()
    print("Upload Start\t:\t"+today.strftime("%H:%M:%S"))

    cursor.executemany(sql_query, val)
    conn.commit()

    today = datetime.datetime.now()
    print("Upload End\t\t:\t"+today.strftime("%H:%M:%S"))
    
def fetch_data(conn, table_name, condition):

    query = 'SELECT * FROM ' + table_name + condition
    # print(query)
    today = datetime.datetime.now()
    print("Download Start\t:\t"+today.strftime("%H:%M:%S"))

    df = pd.read_sql_query(query, conn)
    df.to_csv('sql.csv',index=False)

    today = datetime.datetime.now()
    print("Download End\t:\t"+today.strftime("%H:%M:%S"))
    print(df.shape)
    return df

def delete_data(conn, cursor, table_name, condition):
    
    query = "Delete from " + table_name + condition
    print(query)
    
    cursor.execute(query)
    conn.commit()
    
def get_condition(scenario):
    condition  = " where Scenario = '"+ scenario+"'"
    return condition

def upload_data(df, scenario):
    
    condition  = get_condition(scenario)
    
    date_object = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df['TimeStamp'] = str(date_object)
    df['Scenario'] = scenario
    print('uploading')
    
    conn, cursor = get_sql_connection()
    delete_data(conn, cursor, upload_table_name, condition)
    sql_query, val = genetate_query(df, upload_table_name)
    execute_query(conn, cursor, sql_query, val)
    close_sql_connection(conn)

def download_data(scenario):
    condition  = get_condition(scenario)
    
    conn, cursor = get_sql_connection()
    df = fetch_data(conn, table_name=download_table_name , condition=condition)
    close_sql_connection(conn)
    print(df)
    return df

download_table_name = "Tbl_Dash_Test"
upload_table_name = "Tbl_Dash_Test"

# conn, cursor = get_sql_connection()
# condition  = get_condition("Baseline")
# df = fetch_data(table_name=download_table_name , condition=condition)
# print(df)

# download_data('Baseline')
# download_data('Scenario-1')

# df = pd.read_csv("data/data.csv")
# upload_data(df, 'Scenario-2')

# date_object = datetime.date.today()
# df['TimeStamp'] = str(date_object)
# df['Scenario'] = 'Scenario-1'
# print(df)

# sql_query, val = genetate_query(df, upload_table_name)
# execute_query(conn, cursor, sql_query, val)
# close_sql_connection(conn)
