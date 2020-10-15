import requests
import json
from internal.config import *

def put_new_doc(doc,db):
    id= requests.get('http://db:5984/_uuids').json()['uuids'][0]
    r=requests.put(f'http://{user}:{password}@db:5984/{db}/{id}',data=json.dumps(doc)).json()
    if r.get('ok'):
        return id
    raise Exception

def get_symb_list():
    r=requests.get(f'http://{user}:{password}@db:5984/{db}/_design/getCustomerStockIntrests/_view/symbList').json()
    if r.get('rows'):
        return set([d['key'] for d in r['rows']])


