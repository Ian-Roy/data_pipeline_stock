import os
import requests
import datetime as dt
import json

user = os.getenv('COUCHDB_USER')
password = os.getenv('COUCHDB_PASSWORD')
db_name = os.getenv('COUCHDB_DATABASE_NAME')
def get_symb_list():
    r=requests.get(f'http://{user}:{password}@{db_name}:5984/stock-data/_design/getCustomerStockIntrests/_view/symbList').json()
    return set([d['key'] for d in r['rows']])

def put_new_doc(doc,db):
    id= requests.get(f'http://{db_name}:5984/_uuids').json()['uuids'][0]
    doc['modified_date']= dt.date.today().strftime('%Y-%m-%d')
    r=requests.put(f'http://{user}:{password}@{db_name}:5984/{db}/{id}',data=json.dumps(doc)).json()
    if r.get('ok'):
        print(f'new doc added at id {id}')
        return id
    return None
    
def update_doc(doc,db,id):
    doc['modified_date']= dt.date.today().strftime('%Y-%m-%d')
    print(doc['_rev'])
    r=requests.put(f'http://{user}:{password}@{db_name}:5984/{db}/{id}',data=json.dumps(doc)).json()
    if r.get('ok'):
        print(f"doc id: {id} updated. old rev was: {doc['_rev']}")
        return id
    return None


def get_cache_data(symb):
    r=requests.get(f'http://{user}:{password}@{db_name}:5984/stock-data/_design/getCurentSymb/_view/CurentSymbDataList?key="{symb}"').json()
    if r.get('rows') and len(r.get('rows')) ==1 :
        data= r['rows'][0]
        rj=requests.get(f'http://{user}:{password}@{db_name}:5984/stock-data/{data["id"]}').json()
        return rj
    else:
        return {}

def put_notification_doc(doc):
    symb = doc['symb']
    r=requests.get(f'http://{user}:{password}@{db_name}:5984/stock-data/_design/getCurentSymb/_view/get_notification_list?key="{symb}"').json()
    if r['rows']:
        doc_id =  r['rows'][0]['id']
        old_doc=requests.get(f'http://{user}:{password}@{db_name}:5984/stock-data/{doc_id}').json()
        event_keys = [k for k in old_doc.keys() if 'event_dates' in k]
        for event in event_keys:
            event_list = old_doc[event]
            if doc.get(event):
                event_list.extend(doc[event])
            
            doc[event]=list(set(event_list))
            
        
        doc["_id"]=doc_id
        doc["_rev"]=r['rows'][0]['value']
        
        update_doc(doc,'stock-data',doc["_id"])
        return doc["_id"]
    else:
        return put_new_doc(doc,'stock-data')