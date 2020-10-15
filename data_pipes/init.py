from couch_db import *


user = os.getenv('COUCHDB_USER')
password = os.getenv('COUCHDB_PASSWORD')
db_name = os.getenv('COUCHDB_DATABASE_NAME')

customer1={

  "type": "customer",
  "symb_list": [
    "ADI",
    "NVDA",
    "NRG",
    "GOOG",
    "KIM",
    "stx",
    "orcl",
    "nflx",
    "MED",
    "NLOK"
  ],
  "name": "yada yada"
}


customer2={
  "type": "customer",
  "symb_list": [
    "ibm",
    "KIRK",
    "amd",
    "twtr",
    "wdc",
    "stx",
    "TSLA",
    "nflx",
    "dis",
    "DKNG"
  ],
  "name": "test acc"
}

customer3={
  "type": "customer",
  "symb_list": [
    "ibm",
    "aapl",
    "amd",
    "twtr",
    "wdc",
    "stx",
    "orcl",
    "nflx",
    "dis",
    "sbux"
  ],
  "name": "test acc"
}



dd1={
  "_id": "_design/getCurentSymb",
  "views": {
    "CurentSymbDataList": {
      "map": "function (doc) {\n  if(doc.type == 'price_data'){\n    emit(doc[\"Meta Data\"][ \"2. Symbol\"],doc['modified_date'])\n  }\n}"
    },
    "get_notification_list": {
      "map": "function (doc) {\n  if (doc.type=='notification'){\n    emit(doc.symb, doc._rev);\n  }\n}"
    }
  },
  "language": "javascript"
}

dd2={
  "_id": "_design/getCustomerStockIntrests",
  "views": {
    "symbList": {
      "map": "function (doc) {\n  if(doc.type=='customer'){\n    for (const i in doc.symb_list){\n      emit(doc.symb_list[i].toLowerCase());\n    }\n  }\n}"
    }
  },
  "language": "javascript"
}

requests.put(f'http://{user}:{password}@{db_name}:5984/stock-data')
put_new_doc(customer1,'stock-data')
put_new_doc(customer2,'stock-data')
put_new_doc(customer3,'stock-data')

requests.put(f'http://{user}:{password}@{db_name}:5984/stock-data/_design/getCurentSymb',data=json.dumps(dd1))

requests.put(f'http://{user}:{password}@{db_name}:5984/stock-data/_design/getCustomerStockIntrests',data=json.dumps(dd2))


