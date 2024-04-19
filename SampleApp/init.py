import sqlite3
import bcrypt

import random

def generate_unique_id():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    while True:
        new_id = random.randint(1000, 9999)  # Generate a new random ID
        cursor.execute(f"SELECT COUNT(*) FROM unique_ids WHERE id = ?", (new_id,))
        count = cursor.fetchone()[0]
        if count == 0:  # If the ID is not in use, break the loop
            break
    conn.close()
    return new_id

def add_librarian(username, password, first_name, last_name, email, phone):
    try:
        user_id = generate_unique_id()
        # Connect to the SQLite database
        conn = sqlite3.connect('library.db')
        print("connected to database")
        cursor = conn.cursor()

        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        print("password hashed")
        # Insert the new librarian into the librarians table
        cursor.execute(
            "INSERT INTO librarians (id, username, password, first_name, last_name, email, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, username, password_hash, first_name, last_name, email, phone))
        print("user added")
        # Commit the changes
        conn.commit()
        print("Librarian added successfully.")

    except sqlite3.Error as e:
        print("Error adding librarian:", e)

    finally:
        # Close the connection
        if conn:
            conn.close()

def add_patron(username, password, first_name, last_name, email, phone):
    try:
        user_id = generate_unique_id()
        # Connect to the SQLite database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new patron into the patrons table
        cursor.execute(
            "INSERT INTO patrons (id, username, password, first_name, last_name, email, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, username, password_hash, first_name, last_name, email, phone))

        # Commit the changes
        conn.commit()
        print("Patron added successfully.")

    except sqlite3.Error as e:
        print("Error adding patron:", e)

    finally:
        # Close the connection
        if conn:
            conn.close()

def add_lib_item(title, item_type, author_director_artist, genre, available):
    try:
        user_id = generate_unique_id()
        # Connect to the SQLite database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Insert the new library item into the lib_items table
        cursor.execute(
            "INSERT INTO lib_items (id, title, type, author_director_artist, genre, available) VALUES (?, ?, ?, ?, ?, ?)",
            (id, title, item_type, author_director_artist, genre, available))

        # Commit the changes
        conn.commit()
        print("Library item added successfully.")

    except sqlite3.Error as e:
        print("Error adding library item:", e)

    finally:
        # Close the connection
        if conn:
            conn.close()

def find_user_by_id(user_id):
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        query = "SELECT * FROM patrons WHERE id = ?"
        cursor.execute(query, (user_id,))
        patron_data = cursor.fetchone()
                
        return patron_data
    except Exception as e:
        print("Error finding user:", e)
        return None

def find_checkouts_by_user_id(user_id):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Execute a SQL query to retrieve checked out items by user ID
        cursor.execute('''
            SELECT lib_items.title, lib_items.type, lib_items.author_director_artist, lib_items.genre
            FROM lib_items WHERE checked_out_by = ?''', (user_id,))

        # Fetch all rows from the result set
        checked_out_items = cursor.fetchall()

        return checked_out_items

    except sqlite3.Error as e:
        print("Error finding checked out items by user ID:", e)
        return None

    finally:
        # Close the database connection
        if conn:
            conn.close()

def sys_init():
   # Connect to an SQLite database
   conn = sqlite3.connect('library.db')
   cursor = conn.cursor()

   # Create a table if it doesn't exist for librarians
   cursor.execute('''
        CREATE TABLE IF NOT EXISTS librarians (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            user_type TEXT DEFAULT 'librarian',
            checkouts INTEGER DEFAULT 0
        )
    ''')

    # Create a table if it doesn't exist for patrons
   cursor.execute('''
        CREATE TABLE IF NOT EXISTS patrons (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            user_type TEXT DEFAULT 'patron',
            checkouts INTEGER DEFAULT 0
        )
    ''')

    # Create a table if it doesn't exist for library items
   cursor.execute('''
        CREATE TABLE IF NOT EXISTS lib_items (
            id INTEGER PRIMARY KEY,
            title TEXT,
            type TEXT,
            author_director_artist TEXT,
            genre TEXT,
            available INTEGER DEFAULT 0,
            checked_out_by INTEGER DEFAULT 0
        )
    ''')

   cursor.execute('''
        CREATE TABLE IF NOT EXISTS unique_ids (
            id INTEGER PRIMARY KEY
        )
    ''')

   # Insert some dummy data with hashed passwords
   password1_hash = bcrypt.hashpw(b'secret1', bcrypt.gensalt())
   password2_hash = bcrypt.hashpw(b'secret2', bcrypt.gensalt())
   cursor.execute(
       "INSERT INTO librarians (username, password, first_name, last_name, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
       ('user1', password1_hash, 'John', 'Doe', 'john@example.com',
        '1234567890'))
   
   # Commit the changes
   conn.commit()

   # Close the connection
   conn.close()