import sys
import mysql.connector
from mysql.connector import Error
import hashlib
from config import DB_CONFIG, ADMIN_DEFAULT_USERNAME, ADMIN_DEFAULT_PASSWORD


class Database:
    """Handle MySQL database connections and basic operations."""
    
    def __init__(self, host='localhost', user='root', password='', database='knowledge_system'):
        """Initialize database connection parameters."""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.init_database()

    def get_connection(self):
        """Get active MySQL connection."""
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return conn
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            sys.exit(1)

    def init_database(self):
        """Create database and tables if not exist."""
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = conn.cursor()
            
            # Create database
            cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.database}')
            cursor.execute(f'USE {self.database}')
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    item_type VARCHAR(50) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create genres table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS genres (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT NOT NULL,
                    genre VARCHAR(100) NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database initialized successfully")
        except Error as e:
            print(f"❌ Error initializing database: {e}")
            sys.exit(1)

   