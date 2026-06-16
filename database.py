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
            print(f"Error connecting to MySQL: {e}")
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
            print(f"Error initializing database: {e}")
            sys.exit(1)

    @staticmethod
    def hash_password(password):
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        """Register new user account."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            hashed_password = self.hash_password(password)
            cursor.execute(
                'INSERT INTO users (username, password, role) VALUES (%s, %s, %s)',
                (username, hashed_password, 'user')
            )
            conn.commit()
            return True
        except Error as e:
            if "Duplicate entry" in str(e):
                return False
            print(f"Error: {e}")
            return False
        finally:
            conn.close()
  
    def authenticate(self, username, password):
        """Verify username and password."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        hashed_password = self.hash_password(password)
        cursor.execute(
            'SELECT id, role FROM users WHERE username = %s AND password = %s',
            (username, hashed_password)
        )
        result = cursor.fetchone()
        conn.close()
        return result

    def seed_admin_user(self):
        """Create admin user if not exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (ADMIN_DEFAULT_USERNAME,))
        if not cursor.fetchone():
            admin_password = self.hash_password(ADMIN_DEFAULT_PASSWORD)
            cursor.execute(
                'INSERT INTO users (username, password, role) VALUES (%s, %s, %s)',
                (ADMIN_DEFAULT_USERNAME, admin_password, 'admin')
            )
            conn.commit()
        conn.close()

    def create_item(self, title, item_type, author, genres, description):
        """Create new item with genres."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO items (title, item_type, author, description) VALUES (%s, %s, %s, %s)',
                (title, item_type, author, description)
            )
            item_id = cursor.lastrowid
            
            for genre in genres:
                if genre.strip():
                    cursor.execute(
                        'INSERT INTO genres (item_id, genre) VALUES (%s, %s)',
                        (item_id, genre.strip())
                    )
            
            conn.commit()
            return item_id
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            conn.close()

    def get_all_items(self):
        """Get all items from database."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM items ORDER BY id')
        items = cursor.fetchall()
        
        result = []
        for item in items:
            cursor.execute('SELECT genre FROM genres WHERE item_id = %s', (item['id'],))
            genres = [g['genre'] for g in cursor.fetchall()]
            result.append({
                'id': item['id'],
                'title': item['title'],
                'type': item['item_type'],
                'author': item['author'],
                'genres': genres,
                'description': item['description']
            })
        
        conn.close()
        return result

    def get_item(self, item_id):
        """Get specific item by ID."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM items WHERE id = %s', (item_id,))
        item = cursor.fetchone()
        
        if not item:
            conn.close()
            return None
        
        cursor.execute('SELECT genre FROM genres WHERE item_id = %s', (item_id,))
        genres = [g['genre'] for g in cursor.fetchall()]
        
        conn.close()
        return {
            'id': item['id'],
            'title': item['title'],
            'type': item['item_type'],
            'author': item['author'],
            'genres': genres,
            'description': item['description']
        }

    def update_item(self, item_id, title=None, item_type=None, author=None, genres=None, description=None):
        """Update existing item."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        item = self.get_item(item_id)
        if not item:
            conn.close()
            return False
        
        title = title if title else item['title']
        item_type = item_type if item_type else item['type']
        author = author if author else item['author']
        description = description if description is not None else item['description']
        
        try:
            cursor.execute(
                'UPDATE items SET title = %s, item_type = %s, author = %s, description = %s WHERE id = %s',
                (title, item_type, author, description, item_id)
            )
            
            if genres is not None:
                cursor.execute('DELETE FROM genres WHERE item_id = %s', (item_id,))
                for genre in genres:
                    if genre.strip():
                        cursor.execute(
                            'INSERT INTO genres (item_id, genre) VALUES (%s, %s)',
                            (item_id, genre.strip())
                        )
            
            conn.commit()
            return True
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()

    def delete_item(self, item_id):
        """Delete item by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM items WHERE id = %s', (item_id,))
            conn.commit()
            return True
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()

    def search_items(self, query):
        """Search items by title."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM items WHERE title LIKE %s ORDER BY id', (f'%{query}%',))
        items = cursor.fetchall()
        
        result = []
        for item in items:
            cursor.execute('SELECT genre FROM genres WHERE item_id = %s', (item['id'],))
            genres = [g['genre'] for g in cursor.fetchall()]
            result.append({
                'id': item['id'],
                'title': item['title'],
                'type': item['item_type'],
                'author': item['author'],
                'genres': genres,
                'description': item['description']
            })
        
        conn.close()
        return result

    def search_by_genre_or_author(self, keywords):
        """Search items by genre or author."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        placeholders = ','.join(['%s' for _ in keywords])
        query = f'''
            SELECT DISTINCT i.* FROM items i
            LEFT JOIN genres g ON i.id = g.item_id
            WHERE i.author IN ({placeholders}) OR g.genre IN ({placeholders})
            ORDER BY i.id
        '''
        cursor.execute(query, keywords + keywords)
        
        items = cursor.fetchall()
        
        result = []
        for item in items:
            cursor.execute('SELECT genre FROM genres WHERE item_id = %s', (item['id'],))
            genres = [g['genre'] for g in cursor.fetchall()]
            result.append({
                'id': item['id'],
                'title': item['title'],
                'type': item['item_type'],
                'author': item['author'],
                'genres': genres,
                'description': item['description']
            })
        
        conn.close()
        return result

