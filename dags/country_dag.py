from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import taskinstance
from datetime import datetime
import requests
import json
import mysql.connector

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 4, 3, 10, 0, 0),
    'retries': 1,
}

dag = DAG('country',
            default_args=default_args,
            schedule_interval='0 10 * * *')

#Task_0
def start():
    print("DAG has been started at: {}".format(datetime.now()))

#Task_1
def read():
    country = requests.get("http://country.io/names.json")
    country_names = json.loads(country.text)
    return country_names

#Task_2
def to_db():
    
    country_names = taskinstance.xcom_pull(task_ids='read_json_task')

    try:
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            passwd="1234",
        )

        mycursor = mydb.cursor()

        mycursor.execute("CREATE DATABASE IF NOT EXISTS x")
        mycursor.execute("USE x")
        mycursor.execute("CREATE TABLE IF NOT EXISTS x (id INT AUTO_INCREMENT PRIMARY KEY, country VARCHAR(255), currency VARCHAR(255))")

        for key, value in country_names.items():
            mycursor.execute("INSERT INTO x (country, currency) VALUES (%s, %s)", (country[key], value))

        mydb.commit()
        print("Process completed with success.")

    except mysql.connector.Error as error:
        print("Error: {}".format(error))

    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed.")

#Task_3
def end():
    print("DAG has been completed at: {}".format(datetime.now()))

start_task = PythonOperator(task_id='start_task', python_callable=start, dag=dag)
read_json_task = PythonOperator(task_id='read_json_task', python_callable=read, dag=dag)
to_db_task = PythonOperator(task_id='to_db_task', python_callable=to_db, dag=dag)
end_task = PythonOperator(task_id='end_task', python_callable=end, dag=dag)

start_task >> read_json_task >> to_db_task >> end_task