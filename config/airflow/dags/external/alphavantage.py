import pandas as pd
import requests
import datetime as dt
import json 
import io
import time 

from internal.couch_db import *
from external.config import alphavantage_api_key as api_key

from dask.distributed import Client
client = Client('tcp://dask_scheduler:8786')



def get_compact_historical(symb):
    print(symb)
    r=requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symb}&outputsize=full&apikey={api_key}")
    data=r.json()
    if data.get('Error Message'):
        return data
    data['type']='price_data'
    doc_id=put_new_doc(data,'stock-data')
    return f"doc put {doc_id}"

def get_full_historical(symb):
    data = requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symb}&outputsize=full&apikey={api_key}").json()
    if data.get('Error Message'):
        print(data)
        return None



def get_data_for(symb):
    rj=requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symb}&outputsize=full&apikey={api_key}").json()
    if rj.get('Note'):
        for i in range(1,10):
            time.sleep(20*i)
            rj=requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symb}&outputsize=full&apikey={api_key}").json()
            if rj.get('Time Series (Daily)'):
                break
        else:
            pass # "api limits"
    if rj.get('Error Message'):
        pass
    f = io.StringIO(json.dumps(rj['Time Series (Daily)']))
    df=pd.read_json(f,orient='index')
    df=df.rename(columns={'4. close':'close', "1. open":'open',"2. high":'high',"3. low":"low","5. volume":"volume"})
#     df['timestamp']=pd.to_datetime(df['timestamp'])
#     df=df.set_index('timestamp')
    df=df.sort_index()
    return df
    

def get_mavg_for(df,symb,days=[7,21,63]):
    this_year=dt.datetime.today().year
    df_list=[]
    names=[f"{symb}_{x}_day" for x in days]
    for day in days:
        df_list.append(df['close'].rolling(day).mean())
    mac_df= pd.concat(df_list,axis=1,keys=names).loc[f'{this_year-1}-01-01':]
    return mac_df

def find_intersects(df,t=0.1):
    return df[   
          (abs(df.iloc[:,0]-df.iloc[:,1])<0.1)
        | (abs(df.iloc[:,1]-df.iloc[:,2])<0.1)
        | (abs(df.iloc[:,0]-df.iloc[:,2])<0.1)
    ]
    

def schedule_price_grab(**context):
    ti = context['ti']
    d= ti.xcom_pull(task_ids='get_symb_list')
    symb_list=context['task_instance'].xcom_pull(task_ids='get_symb_list')
    return d
    # output=[]
    # for symb in symb_list:
    #     get_d = client.submit(get_data_for, symb)
    #     get_ma = client.submit(get_mavg_for,get_d,symb)
    #     get_int = client.submit(find_intersects,get_ma)
    #     output.append(get_int)
    # ou=client.gather(output)
    # return(len(ou))





def get_many_compact_historical(symbol_list):
    return [get_compact_historical(symbol) for symbol in symbol_list]

def does_symbol_have_current_data(symbol):
    data = get_compact_historical(symbol)
    if data:
        return str(data['Meta Data']['3. Last Refreshed']==dt.datetime.today().date().strftime('%Y-%m-%d'))
    return None

    
