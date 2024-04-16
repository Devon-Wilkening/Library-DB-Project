from init import add_librarian, add_patron, add_lib_item, find_user_by_id, find_checkouts_by_user_id

class librarian:
    def __init__(self, id, username, password, first_name, last_name, email, phone_number):
        self.id = id
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number

    def add_librarian(self, id, username, password, first_name, last_name, email, phone_number): 
        '''add a new librarian to the database'''
        add_librarian(username, password, first_name, last_name, email, phone_number)
    
    def add_patron(self, username, password, first_name, last_name, email, phone_number):
        '''add a new patron to the database'''
        add_patron(username, password, first_name, last_name, email, phone_number)
    
    def add_lib_item(self, title, item_type, author_director_artist, genre, availability=True):
        '''add an item (book, cd, dvd, etc.) to the database'''
        add_lib_item(title, item_type, author_director_artist, genre, availability)
    #Rework item search so that this method is called for security. Will have to alter route in app.py
    '''
    def item_search(self, title):
        Search collections and find item based on title.
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()

            # Execute the query to search for items by title
            cursor.execute("SELECT * FROM lib_items WHERE title LIKE ?", ('%' + title + '%',))
            items = cursor.fetchall()

            # Close the connection
            conn.close()

            # Return the search results
            return items

        except sqlite3.Error as e:
            print("Error searching for items:", e)
            return None
    '''
    def find_user_by_id(self, user_id):
        '''search for a user based on library id'''
        find_user_by_id(user_id)
    def find_checkouts_by_user_id(self, user_id):
        '''display all checkouts under a specific user'''
        find_checkouts_by_user_id(user_id)
    def display_all_users():
        '''display all users, both librarians and patrons'''