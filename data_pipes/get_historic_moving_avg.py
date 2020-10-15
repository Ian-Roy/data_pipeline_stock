
from dask.distributed import Client
client = Client('tcp://dask_scheduler:8786')
from dask.distributed import Variable

from couch_db import *
from alpha_advantage import *
from yahoo_finance import *

client.upload_file('config.py')
client.upload_file('couch_db.py')
client.upload_file('alpha_advantage.py')
client.upload_file('yahoo_finance.py')

output=[]
symb_list=get_symb_list()
api_min_limit=init_api_var(client)
for symb in symb_list:
    get_low=client.submit(get_min_for,symb) 
    get_high=client.submit(get_max_for,symb) 
    get_d = client.submit(get_data_for, symb, api_min_limit)
    get_df =client.submit(alpha_avantage_api_to_df, get_d)

    low_df=client.submit(add_row_from_single_value,get_low,get_df)
    high_df=client.submit(add_row_from_single_value,get_high,get_df)

    # do once for low and once for high
    get_ma_high = client.submit(get_mavg_for, high_df, symb)
    get_int_high = client.submit(make_many_charts, get_ma_high)  
    get_doc_high = client.submit(make_notification_doc,get_int_high)
    put_doc_high = client.submit(put_notification_doc,get_doc_high)
    output.append(put_doc_high)

    get_ma_low = client.submit(get_mavg_for, low_df, symb)
    get_int_low = client.submit(make_many_charts, get_ma_low)  
    get_doc_low = client.submit(make_notification_doc,get_int_low)
    put_doc_low = client.submit(put_notification_doc,get_doc_low)
    output.append(put_doc_low)


ou=client.gather(output,'skip')
print(output)
import ipdb; ipdb.set_trace()