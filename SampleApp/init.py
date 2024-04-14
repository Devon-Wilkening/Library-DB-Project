import sqlite3
import bcrypt

def add_librarian(username, password, first_name, last_name, email, phone):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('library.db')
        print("connected to database")
        cursor = conn.cursor()

        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        print("password hashed")
        # Insert the new librarian into the librarians table
        cursor.execute(
            "INSERT INTO librarians (username, password, first_name, last_name, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
            (username, password_hash, first_name, last_name, email, phone))
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
        # Connect to the SQLite database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new patron into the patrons table
        cursor.execute(
            "INSERT INTO patrons (username, password, first_name, last_name, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
            (username, password_hash, first_name, last_name, email, phone))

        # Commit the changes
        conn.commit()
        print("Patron added successfully.")

    except sqlite3.Error as e:
        print("Error adding patron:", e)

    finally:
        # Close the connection
        if conn:
            conn.close()

def add_lib_item(title, item_type, author_director_artist, genre, availability=True):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Insert the new library item into the lib_items table
        cursor.execute(
            "INSERT INTO lib_items (title, type, author_director_artist, genre, availability) VALUES (?, ?, ?, ?, ?)",
            (title, item_type, author_director_artist, genre, availability))

        # Commit the changes
        conn.commit()
        print("Library item added successfully.")

    except sqlite3.Error as e:
        print("Error adding library item:", e)

    finally:
        # Close the connection
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
            genre TEXT
            availability BOOLEAN
        )
    ''')

   # Insert some dummy data with hashed passwords
   password1_hash = bcrypt.hashpw(b'secret1', bcrypt.gensalt())
   password2_hash = bcrypt.hashpw(b'secret2', bcrypt.gensalt())
   cursor.execute(
       "INSERT INTO librarians (username, password, first_name, last_name, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
       ('user1', password1_hash, 'John', 'Doe', 'john@example.com',
        '1234567890'))
   cursor.execute(
       "INSERT INTO patrons (username, password, first_name, last_name, email, phone, user_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
       ('user2', password2_hash, 'Jane', 'Smith', 'jane@example.com',
        '0987654321', 'patron'))

   # Commit the changes
   conn.commit()

   # Close the connection
   conn.close()