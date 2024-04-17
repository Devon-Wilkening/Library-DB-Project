from flask import Flask, render_template, request, jsonify, redirect, session, flash
from user_manage import login, User
from init import sys_init
from librarian import add_librarian, add_patron, add_lib_item, find_user_by_id, find_checkouts_by_user_id
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
    availability = 0
    
    # Add the new library item to the database
    add_lib_item(title, item_type, author_director_artist, genre, availability)
    
    # Flash a success message
    flash('Library item successfully added!', 'success')
    
    # Redirect to the home page (or any other relevant page)
    return redirect('/home')

@app.route('/item_search')
def search_page():
    return render_template('item_search.html')

@app.route('/item_search_results')
def search_results():
    # Get the search query from the URL query parameters
    query = request.args.get('q', '')
    print("Search Query:", query)
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
    # Render the search results page with the search results
    print("Search Results:", search_results)
    return render_template('item_search_results.html', query=query, results=search_results)

# Flask route to display all users
@app.route('/all_users')
def all_users():
    # Connect to the database and execute a query to fetch user data
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patrons UNION SELECT * FROM librarians")
    users_data = cursor.fetchall()

    # Close the database connection
    conn.close()

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
    user_id = session.get('user_id')
    
    # Count how many items the user has already checked out
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM lib_items WHERE checked_out_by = ?", (user_id,))
    num_checked_out = cursor.fetchone()[0]
    conn.close()

    # Check if the user has reached the maximum limit of checked out items
    if num_checked_out >= 5:
        flash("You have reached the maximum limit of checked out items (5).")
        return redirect('/home')

    # Proceed with the checkout
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        # Update the availability of the item in the database
        cursor.execute("UPDATE lib_items SET available = ?, checked_out_by = ? WHERE id = ?", (0, user_id, item_id))
        conn.commit()
        flash("Item checked out successfully!")
    except sqlite3.Error as e:
        print("Error checking out item:", e)
        flash("Failed to check out item. Please try again later.")
    finally:
        if conn:
            conn.close()

    return redirect('/home')  # Redirect to the home page after checkout

@app.route('/user_view_checkouts')
def checkouts():
    # Get the ID of the logged-in user
    user_id = session.get('user.user_id')
    print(session)
    print(user_id)
    # Fetch the checked out items for the user from the database
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lib_items")
    checked_out_items = cursor.fetchall()
    conn.close()
    print("Checkouts:", checked_out_items)
    return render_template('user_view_checkouts.html', checked_out_items=checked_out_items)

@app.route('/checkin', methods=['POST'])
def checkin():
    # Get the item ID to check in from the form data
    item_id = request.form.get('item_id')

    # Update the availability of the item in the database
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE lib_items SET available = ?, checked_out_by = NULL WHERE id = ?", (0, item_id))
    conn.commit()
    conn.close()

    # Redirect the user back to the checkouts page
    return redirect('/user_view_checkouts')


@app.route('/profile')
def profile():
   user_data = session.get('user')

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
          user_type=user_data['user_type']
          )

      print(user.email)

      return render_template('profile.html', user_info=user)
   else:
      return redirect('/home', messages="Error Occurred")

@app.route('/logout')
def logout():
   session.clear()
   return redirect('/')


if __name__ == '__main__':
   app.run(debug=True)