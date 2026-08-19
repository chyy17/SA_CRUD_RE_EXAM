import os

import mysql.connector
from mysql.connector import Error

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "crud_db")


def _server_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def initialize_database():
    """Create the application database and tables when they do not exist."""
    connection = _server_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
    finally:
        cursor.close()
        connection.close()

    connection = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Branch (
                Id INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Email VARCHAR(255) NOT NULL,
                Phone VARCHAR(50) NOT NULL,
                Logo VARCHAR(500) NULL
            ) ENGINE=InnoDB
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Category (
                Id INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Product (
                Id INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Cost DECIMAL(12, 2) NOT NULL,
                Price DECIMAL(12, 2) NOT NULL,
                CategoryId INT NOT NULL,
                BranchId INT NOT NULL,
                CONSTRAINT fk_product_category
                    FOREIGN KEY (CategoryId) REFERENCES Category(Id)
                    ON UPDATE CASCADE ON DELETE RESTRICT,
                CONSTRAINT fk_product_branch
                    FOREIGN KEY (BranchId) REFERENCES Branch(Id)
                    ON UPDATE CASCADE ON DELETE RESTRICT
            ) ENGINE=InnoDB
            """
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_db_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
    except Error:
        raise
