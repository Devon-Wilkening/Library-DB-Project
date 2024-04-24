import sqlite3
import bcrypt

#User class for both librarians and patrons

class User:

    #Initialization of User
    def __init__(self, user_id, username, password_hash, first_name, last_name,
                email, phone, user_type, checkouts=None):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.user_type = user_type
        self.checkouts = checkouts

    #Converts User into JSON dictionary
    def to_json(self):
        user_json = {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "user_type" : self.user_type,
            "checkouts" : self.checkouts
        }
        return user_json


# Function to hash the password
def hash_password(password):
   return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# Function to verify the password
def verify_password(password, hashed_password):
   return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


# User login that checks for username and hashed password. Logs user in if both are correct.
def login(username, password):

    try: 
        # Connect to the library database
        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            # Select any user from patrons table where username is same
            query = "SELECT * FROM patrons WHERE username = ?"
            cursor.execute(query, (username,))
            patron_data = cursor.fetchone()

            # Select user from librarians table where username is same
            query = "SELECT * FROM librarians WHERE username = ?"
            cursor.execute(query, (username,))
            librarian_data = cursor.fetchone()

            # Check if the user exists in either patrons or librarians table
            if patron_data:
                user_data = patron_data
            elif librarian_data:
                user_data = librarian_data
            else:
                return None

            # If user exists, verify password
            stored_password_hash = user_data[2]
            if verify_password(password, stored_password_hash):
                user = User(*user_data)
            else:
                user = None
    # Error handling in the event that user does not exist. 
    except sqlite3.Error as e:
        print("SQLite error:", e)
        user = None

    # Close the connection
    conn.close()
    # Return the user
    return user
   