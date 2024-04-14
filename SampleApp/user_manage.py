import sqlite3
import bcrypt

class User:

    # if u uncomment user_type, add user_type into the () after phone
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

    # add user_type if u add to one above 
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


# Simulating a login functionality with hashed passwords
def login(username, password):

   try: 
      # Connect to the SQLite database
        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            # Query the patrons table for the user
            query = "SELECT * FROM patrons WHERE username = ?"
            cursor.execute(query, (username,))
            patron_data = cursor.fetchone()

            # Query the librarians table for the user
            query = "SELECT * FROM librarians WHERE username = ?"
            cursor.execute(query, (username,))
            librarian_data = cursor.fetchone()

            # Check if the user exists in either patrons or librarians table
            if patron_data:
                user_data = patron_data
                user_type = 'patron'
            elif librarian_data:
                user_data = librarian_data
                user_type = 'librarian'
            else:
                return None

            # If user exists, verify password
            stored_password_hash = user_data[2]
            if verify_password(password, stored_password_hash):
                user = User(*user_data)
                user.user_type = user_type  # Add user_type attribute to differentiate patrons and librarians
            else:
                user = None
   except sqlite3.Error as e:
        print("SQLite error:", e)
        user = None

   # Close the connection
   conn.close()

   return user