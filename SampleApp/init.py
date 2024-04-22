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

def add_librarian(username, password, first_name, last_name, email, phone_number): 
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
                "INSERT INTO librarians (id, username, password, first_name, last_name, email, phone_number) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, username, password_hash, first_name, last_name, email, phone_number))
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
        
def add_patron(username, password, first_name, last_name, email, phone_number):
    try:
        user_id = generate_unique_id()
        # Connect to the SQLite database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new patron into the patrons table
        cursor.execute(
            "INSERT INTO patrons (id, username, password, first_name, last_name, email, phone_number) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, username, password_hash, first_name, last_name, email, phone_number))

        # Commit the changes
        conn.commit()
        print("Patron added successfully.")

    except sqlite3.Error as e:
        print("Error adding patron:", e)

    finally:
        # Close the connection
        if conn:
            conn.close()

def add_lib_item(title, item_type, author_director_artist, genre, available=True):
    try:
        id = generate_unique_id()
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

def display_all_users():
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patrons UNION SELECT * FROM librarians")
        users_data = cursor.fetchall()
        conn.close()
        return users_data
    except sqlite3.Error as e:
        # Log the error
        print("Error fetching user data:", e)
        # Handle the error as needed, such as returning an empty list or raising an exception
        return []

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

def checkout_library_item(user_id, item_id):
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Check if the user has reached the maximum limit of checked out items
        cursor.execute("SELECT COUNT(*) FROM lib_items WHERE checked_out_by = ?", (user_id,))
        num_checked_out = cursor.fetchone()[0]
        if num_checked_out >= 5:
            return False, "You have reached the maximum limit of checked out items (5)."

        # Update the availability of the item in the database
        cursor.execute("UPDATE lib_items SET available = ?, checked_out_by = ? WHERE id = ?", (False, user_id, item_id))
        # Update number of checkouts that the user has
        cursor.execute("SELECT checkouts FROM patrons WHERE id = ?", (user_id,))
        checkouts = cursor.fetchone()[0]
        cursor.execute("UPDATE patrons SET checkouts = ? WHERE id = ?", (checkouts + 1, user_id))
        conn.commit()
        return True, "Item checked out successfully!"
    except sqlite3.Error as e:
        print("Error checking out item:", e)
        return False, "Failed to check out item. Please try again later."
    finally:
        if conn:
            conn.close()

def checkin_library_items(user_id, item_id):
    try:
        # Update the availability of the item in the database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE lib_items SET available = ?, checked_out_by = NULL WHERE id = ?", (True, item_id))
        cursor.execute("SELECT checkouts FROM patrons WHERE id = ?", (user_id,))
        checkouts = cursor.fetchone()[0]
        cursor.execute("UPDATE patrons SET checkouts = ? WHERE id = ?", (checkouts - 1, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print("Failed to check in item.")
    finally:
        if conn:
            conn.close()

def get_checked_out_items(user_id):
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Fetch the checked out items for the user from the database
        cursor.execute("SELECT * FROM lib_items WHERE checked_out_by = ?", (user_id,))
        checked_out_items = cursor.fetchall()
        return checked_out_items
    except sqlite3.Error as e:
        print("Error fetching checked out items:", e)
        return []
    finally:
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
            phone_number TEXT,
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
            phone_number TEXT,
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
            available BOOLEAN DEFAULT TRUE,
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
   cursor.execute(
       "INSERT INTO librarians (username, password, first_name, last_name, email, phone_number) VALUES (?, ?, ?, ?, ?, ?)",
       ('user1', password1_hash, 'John', 'Doe', 'john@example.com',
        '1234567890'))
   
   # Commit the changes
   conn.commit()

   # Close the connection
   conn.close()