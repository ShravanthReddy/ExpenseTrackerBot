from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

API_KEY = os.getenv('API_KEY')
PASSWORD = os.getenv("Password")
mydb = mysql.connector.connect(host="localhost", user="root", passwd=PASSWORD, database="sql_expensebot")
mycursor = mydb.cursor()