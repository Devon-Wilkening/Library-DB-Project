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

      response_data = {'status': 'ok', 'user': user.to_json()}

   return jsonify(response_data)

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

@app.route('/add_librarian')
def add_librarian_page():
    return render_template('add_librarian.html')

@app.route('/submit_librarian', methods=['POST'])
def submit_librarian():
    # Extract form data
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    # Add the new librarian to the database
    add_librarian(username, password, first_name, last_name, email, phone)
    # Flash a success message
    flash('Librarian successfully added!', 'success')
    # Redirect to the home page
    return redirect('/home')

@app.route('/add_patron')
def add_patron_page():
    return render_template('add_patron.html')

@app.route('/submit_patron', methods=['POST'])
def submit_patron():
    # Extract form data
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
    # Redirect to the home page (or any other relevant page)
    return redirect('/home')

@app.route('/add_lib_item')
def add_lib_item_page():
   return render_template('add_lib_item.html')

@app.route('/submit_library_item', methods=['POST'])
def submit_library_item():
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
    
    # Redirect to the home page (or any other relevant page)
    return redirect('/home')

@app.route('/item_search')
def search_page():
    return render_template('item_search.html')

@app.route('/item_search_results')
def search_results():
    try:
        # Get the search query from the URL query parameters
        query = request.args.get('q', '')

        # Perform the search in your database
        # Here, you can use SQL queries or any other method to search for items based on the query

        # For example, if you're using SQLite, you can perform a LIKE query
        search_results = []

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

    except Exception as e:
        # Handle any unexpected errors
        flash("An unexpected error occurred: {}".format(e), 'error')
        return redirect('/home')
# Flask route to display all users
@app.route('/all_users')
def all_users():
    
    users_data = display_all_users()
    # Render a template and pass the user data to it
    return render_template('all_users.html', users=users_data)

@app.route('/user_search', methods=['GET', 'POST'])
def search_user():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user = None
        items_checked_out = None
        # Query the database to find the user by ID
        
        user = find_user_by_id(user_id)
        print(user)
        if user:
            # Query the database to find the items checked out by the user
            # Assuming you have a function to retrieve checked out items by user ID
            items_checked_out = find_checkouts_by_user_id(user_id)
            print(items_checked_out)
        return render_template('user_search_results.html', user=user, items_checked_out=items_checked_out)
    
    return render_template('user_search.html')

@app.route('/checkout', methods=['POST'])
def checkout():
    # Get the item ID from the form data
    item_id = request.form.get('item_id')
    
    # Get the ID of the logged-in user (assuming you have implemented user authentication)
    user_id = session['user']['id']
    
    # Call the checkout function
    success, message = checkout_library_item(user_id, item_id)

    if not success:
        flash(message)
    else:
        flash(message, 'success')

    return redirect('/home')  # Redirect to the home page after checkout

@app.route('/user_view_checkouts')
def checkouts():
    # Get the ID of the logged-in user
    user_id = session['user']['id']
    
    # Call the function to fetch checked out items for the user
    checked_out_items = get_checked_out_items(user_id)
    
    return render_template('user_view_checkouts.html', checked_out_items=checked_out_items)

@app.route('/checkin', methods=['POST'])
def checkin():
    # Get the item ID to check in from the form data
    item_id = request.form.get('item_id')

    user_id = session['user']['id']

    checkin_library_items(user_id, item_id)

    # Redirect the user back to the checkouts page
    return redirect('/user_view_checkouts')

@app.route('/logout')
def logout():
   session.clear()
   return redirect('/')

if __name__ == '__main__':
   app.run(debug=True)