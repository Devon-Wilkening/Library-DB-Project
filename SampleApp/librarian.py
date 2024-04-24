from init import add_librarian, add_patron, add_lib_item, display_all_users, find_user_by_id, find_checkouts_by_user_id

#Houses all functions unique to librarians. Prevents import cycling. 

class librarian:
    
    def add_librarian(username, password, first_name, last_name, email, phone_number):
        add_librarian(username, password, first_name, last_name, email, phone_number)

    def add_patron(username, password, first_name, last_name, email, phone_number):
        add_patron(username, password, first_name, last_name, email, phone_number)

    def add_lib_item(title, item_type, author_director_artist, genre, available=True):
        add_lib_item(title, item_type, author_director_artist, genre, available=True)

    def display_all_users():
        display_all_users()

    def find_user_by_id(user_id):
        find_user_by_id(user_id)

    def find_checkouts_by_user_id(user_id):
        find_checkouts_by_user_id(user_id)
