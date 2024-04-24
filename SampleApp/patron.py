from init import checkout_library_item, get_checked_out_items

#Houses all functions unique to patrons. Prevents import cycling. 

class patron:
    
    def checkout_library_item(user_id, item_id):
        checkout_library_item(user_id, item_id)

    def get_checked_out_items(user_id):
        get_checked_out_items(user_id)

    def checkin_library_items(user_id, item_id):
        checkin_library_items(user_id, item_id)