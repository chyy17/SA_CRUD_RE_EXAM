import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root ', 
        password='sokouchy',  
        database='crud_db' 
    )
