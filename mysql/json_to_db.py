import requests
import json
import mysql.connector

currency = requests.get("http://country.io/currency.json")
country = requests.get("http://country.io/names.json")

currency = json.loads(currency.text)
country = json.loads(country.text)

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

    for key, value in currency.items():
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
