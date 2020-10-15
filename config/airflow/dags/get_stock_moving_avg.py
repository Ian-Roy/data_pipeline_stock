from datetime import timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

from external.alphavantage import *
from internal.couch_db import *
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(seconds=30),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
dag = DAG(
    'get_stock_moving_average',
    default_args=default_args,
    description='get stock data',
    schedule_interval=timedelta(days=1),
)


# def print_context(ds, **kwargs):
#     print(kwargs)
#     print(ds)
#     return 'Whatever you return gets printed in the logs'


symb_list = PythonOperator(
    task_id='get_symb_list',
    provide_context=True,
    python_callable=get_symb_list,
    dag=dag,
)
# # t1, t2 and t3 are examples of tasks created by instantiating operators
# tl=[]
# for symb in ['ibm','aapl']:
#     task = PythonOperator(
#         task_id=f'get-for_{symb}',
#         python_callable=get_compact_historical,
#         op_kwargs={'symb': symb},
#         dag=dag,
#     )
#     tl.append(task)
# symb_list >> tl

get_data = PythonOperator(
    task_id='get_stock_data',
    provide_context=True,
    python_callable=schedule_price_grab,
    dag=dag,
)
symb_list >> get_data