from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import taskinstance
from datetime import datetime
import requests
import json
import mysql.connector

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 4, 3, 10, 0, 0),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
}

dag = DAG(
    'data_merge',
    default_args=default_args,
    schedule_interval='0 11 * * *',
)

#Task_0
def start():
    print("DAG has been started at: {}".format(datetime.now()))

#Task_1
def merge_country_currency():

    try:
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            passwd="1234",
            database="x"
        )

        mycursor = mydb.cursor()

        mycursor.execute("CREATE TABLE IF NOT EXISTS data_merge LIKE country")
        mycursor.execute("ALTER TABLE data_merge ADD COLUMN currency VARCHAR(255)")

        mycursor.execute("DELETE FROM data_merge")

        mycursor.execute("INSERT INTO data_merge (country, currency) SELECT country, currency FROM country")

        mydb.commit()
        print("Process completed with success.")

    except mysql.connector.Error as error:
        print("Error: {}".format(error))

    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed.")

#Task_2
def end():
    print("DAG has been finished at: {}".format(datetime.now()))

start_task = PythonOperator(task_id='start_task', python_callable=start, dag=dag)
merge_country_currency_task = PythonOperator(task_id='merge_country_currency_task', python_callable=merge_country_currency, dag=dag)
end_task = PythonOperator(task_id='end_task', python_callable=end, dag=dag)

start_task >> merge_country_currency_task >> end_task