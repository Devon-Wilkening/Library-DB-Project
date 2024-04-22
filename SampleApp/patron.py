from init import checkout_library_item, get_checked_out_items

class patron:
    def __init__(self, id, username, password, first_name, last_name, email, phone_number):
        self.id = id
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number

    def checkout_library_item(user_id, item_id):
        checkout_library_item(user_id, item_id)

    def get_checked_out_items(user_id):
        get_checked_out_items(user_id)

    def checkin_library_items(user_id, item_id):
        checkin_library_items(user_id, item_id)