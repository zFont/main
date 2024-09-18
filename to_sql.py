import json
import sqlite3

def create_table_if_not_exists(cursor, create_table_query):
    cursor.execute(create_table_query)

def get_or_insert_category(cursor, category_name):
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        return cursor.lastrowid

def get_or_insert_author(cursor, author_name, author_url):
    cursor.execute("SELECT id FROM author WHERE name = ?", (author_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute("INSERT INTO author (name, url) VALUES (?, ?)", (author_name, author_url))
        return cursor.lastrowid

def json_to_sqlite(data, sqlite_db):
    # Connect to SQLite database (or create it)
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()

    # Create tables
    create_category_table = """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """
    create_author_table = """
    CREATE TABLE IF NOT EXISTS author (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        url TEXT
    );
    """
    create_item_table = """
    CREATE TABLE IF NOT EXISTS item (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        size TEXT NOT NULL,
        thumbnail TEXT NOT NULL,
        author INTEGER,
        category INTEGER NOT NULL,
        preview TEXT,
        url TEXT NOT NULL,
        FOREIGN KEY (author) REFERENCES author(id),
        FOREIGN KEY (category) REFERENCES categories(id)
    );
    """
    create_table_if_not_exists(cursor, create_category_table)
    create_table_if_not_exists(cursor, create_author_table)
    create_table_if_not_exists(cursor, create_item_table)
    
    # Insert data into the tables
    for item in data:
        category_id = get_or_insert_category(cursor, item)
        
        for post in data[item]:
            author_name = post.get("a")
            author_url = post.get('a_l')
            preview = post.get('preview') or post.get('p')
            thumbnail = post.get('thumbnail') or post.get('t')
            size = post.get('size') or post.get('s')
            title = post.get('title') or post.get('n')
            url = post.get('url') or post.get('u')
            
            author_id = None
            if author_name:
                author_id = get_or_insert_author(cursor, author_name, author_url)
            
            cursor.execute("""
                INSERT INTO item (title, size, thumbnail, author, category, preview, url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, size, thumbnail, author_id, category_id, preview, url))
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f"Data successfully saved to {sqlite_db}")