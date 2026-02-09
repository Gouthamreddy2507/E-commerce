import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Codegnan@25',
    database='ecommerce'
)
cursor = db.cursor()
