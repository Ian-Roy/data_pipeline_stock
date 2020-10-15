
import pandas as pd
import random
import datetime as dt
import json 
import io
from config import alphavantage_api_key as api_key
import time 
import base64 
import io 
import requests
from dask.distributed import Variable
import matplotlib.pyplot as plt

from couch_db import *

def init_api_var(client):
    api_min_limit=Variable('alpha_advantage_api_min_limit',client)
    api_min_limit.set(dt.datetime.timestamp(dt.datetime.now())-70)
    return api_min_limit
    

    
def get_data_for(symb,api_min_limit):

    doc=get_cache_data(symb)  

    if doc and doc.get('modified_date')==dt.date.today().strftime('%Y-%m-%d'):
        print("value in db")
        return doc
    else:
        if (dt.datetime.timestamp(dt.datetime.now()) - api_min_limit.get()) < 55:
            rj=requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symb}&outputsize=full&apikey={api_key}").json()
        else:
            for _ in range(10):
                while (dt.datetime.timestamp(dt.datetime.now()) - api_min_limit.get()) < 55:
                    time.sleep(random.random()*2)
                rj=requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symb}&outputsize=full&apikey={api_key}").json()
                if rj.get('Time Series (Daily)'):
                    break
                else:
                    api_min_limit.set(dt.datetime.timestamp(dt.datetime.now()))
            else:
                pass #should do something here we are at the daily limit
                    
                
        if rj.get('Note'):
            api_min_limit.set(dt.datetime.timestamp(dt.datetime.now()))
            for _ in range(10):
                while (dt.datetime.timestamp(dt.datetime.now()) - api_min_limit.get()) < 55:
                    time.sleep(random.random()*2)
                rj=requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symb}&outputsize=full&apikey={api_key}").json()
                if rj.get('Time Series (Daily)'):
                    break
                else:
                    api_min_limit.set(dt.datetime.timestamp(dt.datetime.now()))
            else:
                pass #should do something here we are at the daily limit
        if rj.get('Error Message'):
            print (rj)
            return rj
        rj['type']='price_data'
        if doc.get('_id'):
            print(doc['_id'])
            print(doc.keys())
            doc['Meta Data']=rj['Meta Data']
            doc['Time Series (Daily)']=rj['Time Series (Daily)']
            update_doc(doc,'stock-data', doc['_id'])
            return doc
        else:
            put_new_doc(rj,'stock-data')
            return rj
        
def alpha_avantage_api_to_df(doc):
        f = io.StringIO(json.dumps(doc['Time Series (Daily)']))
        df=pd.read_json(f,orient='index')
        df=df.rename(columns={'4. close':'close', "1. open":'open',"2. high":'high',"3. low":"low","5. volume":"volume"})
        df=df.sort_index()
        return df

def add_row_from_single_value(val,df):
    row = pd.Series({'close':val,'open':val,'high':val,'low':val},name=dt.datetime.today())
    df = df.append(row)
    return df

def get_mavg_for(df,symb,days=[7,21,63]):
    this_year=dt.datetime.today().year
    df_list=[]
    names=[f"{symb}_{x}_day" for x in days]
    for day in days:
        df_list.append(df['close'].rolling(day).mean())
    mac_df= pd.concat(df_list,axis=1,keys=names).loc[f'{this_year-1}-01-01':]
    return mac_df

 
def make_many_charts(df):
    chart_list=[]
    for i in range(len(df.columns)):
        if i == len(df.columns)-1:
            chart_list.append(make_chart(df.iloc[:,[0,i]]))
        else:
            chart_list.append(make_chart(df.iloc[:,[i,i+1]]))
    return chart_list

def make_chart(df):
    int_df= df[
          ((df.iloc[:,0].shift(1)>df.iloc[:,1].shift(1)) & (df.iloc[:,0]<df.iloc[:,1]))
        | ((df.iloc[:,0].shift(1)<df.iloc[:,1].shift(1)) & (df.iloc[:,0]>df.iloc[:,1]))
    ]
    p=df.plot()
    p.scatter(int_df.index, int_df.iloc[:,0],marker='x',color='black')
    p.set_title(f"{df.columns[0]} vs. {df.columns[1]}")
    p.set_ylabel('Price USD ($)')
    p.plot()
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png')
    pic_IObytes.seek(0)
    data_str=base64.encodebytes(pic_IObytes.read()).decode('utf8')
    return (data_str,int_df)

def make_notification_doc(chart_list):
    doc={}
    # chart_list is a list of tupples containing the chart image and the intersection data
    doc['chart_list'] = [x[0] for x in chart_list]
    doc['type'] = 'notification'
    doc['symb'] = chart_list[0][1].columns[0].split('_')[0]
    for obj in chart_list:
        chart= obj[0]
        df=obj[1]
        days1 = df.columns[0].split('_')[1]
        days2 = df.columns[1].split('_')[1]
        event_dates=[d.strftime('%Y-%m-%d') for d in df.index.to_list()]
        doc[f'event_dates_{days1}:{days2}'] = event_dates
    return doc