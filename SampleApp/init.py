import sqlite3
import bcrypt
import random

# Function to create unique id to remove overlap between librarians, patrons, and items. Taken ids are stored in table to prevent reuse.
def generate_unique_id():
    # Connect to database
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    while True:
        # Generate new id, check for use, and return if unused. Otherwise, keep generating for new id.
        new_id = random.randint(1000, 9999)  # Generate a new random ID
        cursor.execute(f"SELECT COUNT(*) FROM unique_ids WHERE id = ?", (new_id,))
        count = cursor.fetchone()[0]
        if count == 0:  # If the ID is not in use, break the loop
            break
    # Close connection to db and return the new id
    conn.close()
    return new_id

# Function to add new librarian to librarian table
def add_librarian(username, password, first_name, last_name, email, phone_number): 
        try:
            # Generate new id to be inserted with other, passed args
            user_id = generate_unique_id()
            # Connect to the database
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
            # Commit the changes
            conn.commit()
            print("Librarian added successfully.")
        # Handle errors if unsuccessful
        except sqlite3.Error as e:
            print("Error adding librarian:", e)

        finally:
            # Close the connection
            if conn:
                conn.close()

# Function to add new patron to the patrons table        
def add_patron(username, password, first_name, last_name, email, phone_number):
    try:
        user_id = generate_unique_id()
        # Connect to the database
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

# Function to add new library item to lib_items table
def add_lib_item(title, item_type, author_director_artist, genre, available=True):
    try:
        id = generate_unique_id()
        # Connect to the database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Insert the new library item into the lib_items table
        cursor.execute(
            "INSERT INTO lib_items (id, title, type, author_director_artist, genre, available) VALUES (?, ?, ?, ?, ?, ?)",
            (id, title, item_type, author_director_artist, genre, available))

        # Commit the changes
        conn.commit()
        print("Library item added successfully.")
    # Handle errors if item not added successfully
    except sqlite3.Error as e:
        print("Error adding library item:", e)

    finally:
        # Close the connection
        if conn:
            conn.close()

#Function to grab all users/user data to be displayed
def display_all_users():
    try:
        # Connect to database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        # Fetch all users in both patrons and librarians tables
        cursor.execute("SELECT * FROM patrons UNION SELECT * FROM librarians")
        users_data = cursor.fetchall() #users_data to hold all of the data for each of the fetched users
        conn.close()
        # Return the user data
        return users_data
    # Error handling
    except sqlite3.Error as e:
        print("Error fetching user data:", e)
        return []

# Function to find any user by their id
def find_user_by_id(user_id):
    try:
        #Connect to database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Check librarian and patron tables for user with matching id
        query = "SELECT * FROM patrons WHERE id = ?"
        cursor.execute(query, (user_id,))
        patron_data = cursor.fetchone()

        query = "SELECT * FROM librarians WHERE id = ?"
        cursor.execute(query, (user_id,))
        librarian_data = cursor.fetchone()
        
        # If id exists in patron, then assign to user_data. Else, if id exists in librarian, assign to user_data
        if patron_data:
            user_data = patron_data
        elif librarian_data:
            user_data = librarian_data
        # Return user data
        return user_data
    # If no user exists with id, return nothing
    except sqlite3.Error as e:
        print("Error finding user:", e)
        return None

#Function to find checkouts associated with a user's id
def find_checkouts_by_user_id(user_id):
    try:
        # Connect to database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Use query to get all items/item info from library items table where checked out by user
        cursor.execute('''
            SELECT lib_items.title, lib_items.type, lib_items.author_director_artist, lib_items.genre
            FROM lib_items WHERE checked_out_by = ?''', (user_id,))

        # Fetch all results
        checked_out_items = cursor.fetchall()
        # Return all fetched items
        return checked_out_items
    # Error handling for problems encountered when checking for items
    except sqlite3.Error as e:
        print("Error finding checked out items by user ID:", e)
        return None

    finally:
        # Close the database connection
        if conn:
            conn.close()

# Function to check out library items as a patron if checkout count has not been exceeded
def checkout_library_item(user_id, item_id):
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Check if the user has reached the maximum limit of checked out items
        cursor.execute("SELECT COUNT(*) FROM lib_items WHERE checked_out_by = ?", (user_id,))
        num_checked_out = cursor.fetchone()[0]
        if num_checked_out >= 5:
            return False, "You have reached the maximum limit of checked out items (5)."

        # Update the availability of the item in the database due to checkout
        cursor.execute("UPDATE lib_items SET available = ?, checked_out_by = ? WHERE id = ?", (False, user_id, item_id))
        # Update number of checkouts that the user has
        cursor.execute("SELECT checkouts FROM patrons WHERE id = ?", (user_id,))
        checkouts = cursor.fetchone()[0]
        cursor.execute("UPDATE patrons SET checkouts = ? WHERE id = ?", (checkouts + 1, user_id))
        conn.commit()
        return True, "Item checked out successfully!"
    except sqlite3.Error as e:
        # Error handling in case checkout cannot be performed
        print("Error checking out item:", e)
        return False, "Failed to check out item. Please try again later."
    finally:
        # Close connection to database
        if conn:
            conn.close()

# Function to check library items back in
def checkin_library_items(user_id, item_id):
    try:
        # Connect to database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        # Update availability of checked in item
        cursor.execute("UPDATE lib_items SET available = ?, checked_out_by = NULL WHERE id = ?", (True, item_id))
        # Update number of checkouts for the user
        cursor.execute("SELECT checkouts FROM patrons WHERE id = ?", (user_id,))
        checkouts = cursor.fetchone()[0]
        cursor.execute("UPDATE patrons SET checkouts = ? WHERE id = ?", (checkouts - 1, user_id))
        conn.commit()
    # Handle errors for failed check-ins
    except sqlite3.Error as e:
        print("Error checking in item:", e)
        return False, "Failed to check in item. Please try again later."
    finally:
        # Close connection to database
        if conn:
            conn.close()

def get_checked_out_items(user_id):
    try:
        # Connect to database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Fetch the checked out items for the user from the database
        cursor.execute("SELECT * FROM lib_items WHERE checked_out_by = ?", (user_id,))
        checked_out_items = cursor.fetchall()
        return checked_out_items
    # Handle errors for getting a user's check-outs
    except sqlite3.Error as e:
        print("Error fetching checked out items:", e)
        return []
    finally:
        # Close connection to database
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
            username TEXT UNIQUE,
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
            username TEXT UNIQUE,
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

    password1_hash = bcrypt.hashpw(b'Librarian1', bcrypt.gensalt())
    cursor.execute(
       "INSERT INTO librarians (username, password, first_name, last_name, email, phone_number) VALUES (?, ?, ?, ?, ?, ?)",
       ('Librarian1', password1_hash, 'John', 'Doe', 'john@example.com','1234567890'))

    password2_hash = bcrypt.hashpw(b'Patron2', bcrypt.gensalt())
    cursor.execute(
       "INSERT INTO patrons (username, password, first_name, last_name, email, phone_number) VALUES (?, ?, ?, ?, ?, ?)",
       ('Patron2', password2_hash, 'John', 'Doe', 'john@example.com','1234567890'))


   # Commit the changes
    conn.commit()

   # Close the connection
    conn.close()
    