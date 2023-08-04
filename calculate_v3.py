# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 18:02:21 2023

@author: ONS2172
"""

import pandas as pd
pd.options.mode.chained_assignment

sort_map = {
    'OPENING STOCK':1,
    'PRODUCTION':2,
    'CLOSING STOCK':3,
    'DIFC':4
    }

def calculate(df):
    df['Key'] = df['SKU'].astype(str) + '_' + df['Scenario']
    nWeek=13
    # print(df)
    df_data = df.drop(['SKU','Country','Region','Scenario'], axis=1)
    df_data = df_data.pivot(index='Key', columns= 'Key Figure')
    df_data.columns = df_data.columns.map('{0[0]}__{0[1]}'.format) 
    # print(df_data)
        
    for i in range(nWeek):
        if i!=0:
            df_data['Week ' + str(i+1) + '__' +'OPENING STOCK'] = df_data['Week ' + str(i) + '__' +'CLOSING STOCK']
        df_data['Week ' + str(i+1) + '__' +'CLOSING STOCK'] = df_data['Week ' + str(i+1) + '__' +'OPENING STOCK'].astype(int) + df_data['Week ' + str(i+1) + '__' +'PRODUCTION'].astype(int) - 200
        df_data['Week ' + str(i+1) + '__' +'CLOSING STOCK'] = df_data['Week ' + str(i+1) + '__' +'CLOSING STOCK'].mask(df_data['Week ' + str(i+1) + '__' +'CLOSING STOCK'] < 0, 0)
        df_data['Week ' + str(i+1) + '__' +'DIFC'] = df_data['Week ' + str(i+1) + '__' +'CLOSING STOCK'] / 200 *7
    
    df1 = df_data[['Week ' + str(i+1) + '__' +'OPENING STOCK' for i in range(13)]]
    df2 = df_data[['Week ' + str(i+1) + '__' +'PRODUCTION' for i in range(13)]]
    df3 = df_data[['Week ' + str(i+1) + '__' +'CLOSING STOCK' for i in range(13)]]
    df4 = df_data[['Week ' + str(i+1) + '__' +'DIFC' for i in range(13)]]
    
    df1['Key Figure'] = 'OPENING STOCK'
    df2['Key Figure'] = 'PRODUCTION'
    df3['Key Figure'] = 'CLOSING STOCK'
    df4['Key Figure'] = 'DIFC'
    
    df1.columns = [item.split('__')[0] for item in df1.columns]
    df2.columns = [item.split('__')[0] for item in df2.columns]
    df3.columns = [item.split('__')[0] for item in df3.columns]
    df4.columns = [item.split('__')[0] for item in df4.columns]
    
    df_final = pd.concat([df1,df2,df3,df4], axis=0)
    df_final['SKU'] = df_final.index
    df_final = df_final.set_index(df_final['SKU'].astype(str) + '_' + df_final['Key Figure'])
    df_final = df_final.drop(['Key Figure','SKU'], axis=1)
    
    df = df.set_index(df['SKU'].astype(str) + '_' + df['Scenario'] + '_' + df['Key Figure'])
    df = df[['SKU','Country','Region','Key Figure','Scenario']]
    df = df_final.join(df)
    df['sort'] = df['Key Figure'].map(sort_map)
    df = df.sort_values(['SKU', 'Scenario', 'sort'])
    df=df[['SKU','Country','Region','Key Figure','Week 1','Week 2','Week 3','Week 4','Week 5','Week 6','Week 7','Week 8','Week 9','Week 10','Week 11','Week 12','Week 13','Scenario']]
    df.reset_index(inplace=True, drop=True)
    for col in ['Week '+str(i+1) for i in range(13)]:
        df[col] = df[col].astype(float)
    # print(df)
    
    return df

# df = pd.read_csv("data/data.csv")
# df = calculate(df)
# print(df.dtypes)
# df.to_csv('a.csv', index=False)