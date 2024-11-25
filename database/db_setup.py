import mysql.connector
from mysql.connector import Error

DATABASE_NAME = "ecommerce_db"

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",  # Update to your MySQL root password
}

TABLES = {
    "customers": """
        CREATE TABLE IF NOT EXISTS customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            age INT,
            address VARCHAR(255),
            gender ENUM('Male', 'Female'),
            marital_status ENUM('Single', 'Married'),
            wallet_balance DECIMAL(10, 2) DEFAULT 0.00
        )
    """,
    "inventory": """
        CREATE TABLE IF NOT EXISTS inventory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category ENUM('Food', 'Clothes', 'Accessories', 'Electronics'),
            price DECIMAL(10, 2) NOT NULL,
            description TEXT,
            stock_count INT NOT NULL
        )
    """,
    "sales": """
        CREATE TABLE IF NOT EXISTS sales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            inventory_id INT NOT NULL,
            quantity INT NOT NULL,
            total_price DECIMAL(10, 2) NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (inventory_id) REFERENCES inventory(id)
        )
    """,
    "reviews": """
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            inventory_id INT NOT NULL,
            rating INT CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (inventory_id) REFERENCES inventory(id)
        )
    """,
}

def create_database_and_tables():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Create the database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        connection.database = DATABASE_NAME
        
        # Create tables
        for table_name, create_table_sql in TABLES.items():
            cursor.execute(create_table_sql)
            print(f"Table `{table_name}` ensured in database `{DATABASE_NAME}`.")
        
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_connection():
    """Establish and return a database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG, database=DATABASE_NAME)
        return connection
    except Error as e:
        print(f"Error while connecting to database: {e}")
        return None

if __name__ == "__main__":
    create_database_and_tables()
