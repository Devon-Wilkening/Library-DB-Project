from flask import Flask, render_template, request, jsonify, redirect, session, flash
from user_manage import login, User
from init import sys_init, add_librarian, add_patron, add_lib_item, display_all_users, find_user_by_id, find_checkouts_by_user_id, checkout_library_item, checkin_library_items, get_checked_out_items, generate_unique_id 
#import goes here
import sqlite3

app = Flask(__name__)

app.secret_key = 'your_secret_key'

with app.app_context():
   sys_init()

@app.route('/')
def index():
   if request.args:
      return render_template(
          'index.html', messages=json.loads(request.args['messages']))
   else:
      return render_template('index.html', messages='')


@app.route('/ajaxkeyvalue', methods=['POST'])
def ajax():
    data = request.json  # Assuming the AJAX request sends JSON data
    print(data)
    # Process the data
    username = data['username']
    password = data['password']

    print(username)
    print(password)
    # Grabs user if login is successful, otherwise fails
    user = login(username, password)
    if not user:
        response_data = {'status': 'fail'}
    else:
        session['logged_in'] = True
        session['username'] = username
        session['user'] = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone,
            'user_type' : user.user_type
        }
        # Returns user to JSON
        response_data = {'status': 'ok', 'user': user.to_json()}

    return jsonify(response_data)
# Route for home page
@app.route('/home')
def home():
    user_data = session.get('user')
    user_type = user_data.get('user_type')

    if user_data:
      # Reconstruct the user object
        user = User(
            user_id=user_data['id'],
            username=user_data['username'],
            password_hash='',
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            phone=user_data['phone'],
            user_type=user_type)

        print(user.email)

        return render_template('home.html', user_info=user)
    else:
        return redirect('/', messages="Please login again!")
# Route to add librarian
@app.route('/add_librarian')
def add_librarian_page():
    return render_template('add_librarian.html')
# Route to submit librarian
@app.route('/submit_librarian', methods=['POST'])
def submit_librarian():
    # RBAC to ensure that user is librarian
    user_type = session['user']['user_type']
    if user_type == 'librarian':
        try:
            # Extract form data
            username = request.form['username']
            password = request.form['password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            phone = request.form['phone']
            # Attempt to add the new librarian to the database
            add_librarian(username, password, first_name, last_name, email, phone)
            # Flash a success message
            flash('Librarian successfully added!', 'success')
        except Exception as e:
            # Flash an error message indicating failure
            print("Error adding librarian:", e)
            flash('Failed to add librarian. Please try again.', 'error')
    else:
        flash('Access denied. Only librarians may add librarians.', 'error')
    
    return redirect('/home')
# Route to add patron
@app.route('/add_patron')
def add_patron_page():
    return render_template('add_patron.html')
# Route for submission of patron
@app.route('/submit_patron', methods=['POST'])
def submit_patron():
    # RBAC to ensure that user is librarian
    user_type = session['user']['user_type']
    if user_type == 'librarian':
        # Extract form data
        try:
            username = request.form['username']
            password = request.form['password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            phone = request.form['phone']
            # Add the new patron to the database
            add_patron(username, password, first_name, last_name, email, phone)
            # Flash a success message
            flash('Patron successfully added!', 'success')
        except Exception as e:
            print("Error adding patron:", e)
            flash('Failed to add patron. Please try again.', 'error')
        # Redirect to the home page (or any other relevant page)
    else:
        flash('Access denied. Only librarians may add patrons', 'error')
    return redirect('/home')
# Route to add lib item
@app.route('/add_lib_item')
def add_lib_item_page():
   return render_template('add_lib_item.html')
# Route for submission of lib items
@app.route('/submit_library_item', methods=['POST'])
def submit_library_item():
    # RBAC to ensure user is librarian
    user_type = session['user']['user_type']
    if user_type == 'librarian':
        try:
            # Extract form data
            title = request.form['title']
            item_type = request.form['item_type']
            author_director_artist = request.form['author_director_artist']
            genre = request.form['genre']
            # Set availability to "Available" by default
            available = True
            
            # Add the new library item to the database
            add_lib_item(title, item_type, author_director_artist, genre, available)
            
            # Flash a success message
            flash('Library item successfully added!', 'success')
        except Exception as e:
            print("Error adding library itemL:", e)
            flash('Failed to add library item. Please try again.', 'error')
        # Redirect to the home page (or any other relevant page)
    else:
        flash('Access denied. Only librarians may add library items.', 'error')
    return redirect('/home')
# Route for item search
@app.route('/item_search')
def search_page():
    return render_template('item_search.html')
# Route for search results 
@app.route('/item_search_results')
def search_results():
    try:
        # Get the search query from the URL query parameters
        query = request.args.get('q', '')

        search_results = []
        # Connect to database and fetch all library items with title similar to query
        if query:
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lib_items WHERE title LIKE ?", ('%' + query + '%',))
            search_results = cursor.fetchall()
            conn.close()

        # Check if search_results is empty and display a flash message
        if not search_results:
            flash("No results found for your query.", 'error')

        # Render the search results page with the search results
        user = session.get('user')
        return render_template('item_search_results.html', query=query, results=search_results, user=user)

    except sqlite3.Error as e:
        # Handle any unexpected errors
        print("Error with item search:", e)
        flash("An unexpected error occurred: {}".format(e), 'error')
        return redirect('/home')
# Route to display all users
@app.route('/all_users')
def all_users():
    # RBAC to ensure only librarians can display all users
    user_type = session['user']['user_type']
    if user_type == 'librarian':
        try:
            # Call function to get all users' data
            users_data = display_all_users()
        except Exception as e:
            print('Error with displaying all users:', e)
    else:
        flash('Access denied. Only librarians may view all users', 'error')
    # Render a template and pass the user data to it
    return render_template('all_users.html', users=users_data)
# Route to search for user 
@app.route('/user_search', methods=['GET', 'POST'])
def search_user():
    # Check for user type. Only allow user search for librarians
    user_type = session['user']['user_type']
    if user_type == 'librarian':
        if request.method == 'POST':
            # Get user id from form
            user_id = request.form.get('user_id')
            user = None
            items_checked_out = None
            # Call function to find user by their user id
            user = find_user_by_id(user_id)
            # If user is found, call function to retrieve all of user's current checkouts
            if user:
                
                items_checked_out = find_checkouts_by_user_id(user_id)
                
            return render_template('user_search_results.html', user=user, items_checked_out=items_checked_out)
        
        return render_template('user_search.html')
    else:
        flash('Access denied. Only librarians may search users.', 'error')
    return render_template('home.html')
# Route to check item out
@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        # Get the item ID from the form data
        item_id = request.form.get('item_id')
        # Get the ID of current, logged-in user 
        user_id = session['user']['id']
        
        # Call the checkout function
        checkout_library_item(user_id, item_id)

        flash('Item successfully checked out', 'success')
    except Exception as e:
        print("Error checking out:". e)
        flash('Error with item checkout. Please try again.')

    return redirect('/home')  # Redirect to the home page after checkout
# Route to allow view of checkouts for user
@app.route('/user_view_checkouts')
def checkouts():
    try:
        # Get the ID of the logged-in user
        user_id = session['user']['id']
        # Call the function to fetch checked out items for the user
        checked_out_items = get_checked_out_items(user_id)
    except Exception as e:
        print("Error checking out:". e)
        print('(Patron): Error viewing checkouts')
    return render_template('user_view_checkouts.html', checked_out_items=checked_out_items)
#Route to check lib item in 
@app.route('/checkin', methods=['POST'])
def checkin():
    try:
        # Get the item ID to check in from the form data
        item_id = request.form.get('item_id')
        # Get the user id from form data
        user_id = session['user']['id']
        # Use check-in function to check item in using item id and user id
        checkin_library_items(user_id, item_id)

        flash('Item successfully checked in.', 'success')
    except Exception as e:
        print("Error with item check-in", e)
        flash('Error with item check-in. Please try again.', 'error')
    # Redirect the user back to the checkouts page
    return redirect('/user_view_checkouts')
# Route to clear session and log user out 
@app.route('/logout')
def logout():
   session.clear()
   return redirect('/')
# Flask debug mode. Turned off unless actively developing for security, prevention of duplicates, etc. 
if __name__ == '__main__':
   app.run(debug=False)