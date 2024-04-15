from flask import Flask, render_template, request, jsonify, redirect, session, flash
from user_manage import login, User
from init import sys_init
from librarian import add_librarian, add_patron, add_lib_item
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
    # Redirect to the home page (or any other relevant page)
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
    availability = True
    
    # Add the new library item to the database
    add_lib_item(title, item_type, author_director_artist, genre, availability)
    
    # Flash a success message
    flash('Library item successfully added!', 'success')
    
    # Redirect to the home page (or any other relevant page)
    return redirect('/home')

@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/search_results')
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
        cursor.execute("SELECT * FROM lib_items")
        search_results = cursor.fetchall()
        conn.close()
    print("Search Results", search_results)
    # Render the search results page with the search results
    return render_template('search_results.html', query=query, results=search_results)

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
          phone=user_data['phone'])

      print(user.email)

      return render_template('profile.html', user_info=user)
   else:
      return redirect('/', messages="Please login again!")

@app.route('/logout')
def logout():
   session.clear()
   return redirect('/')


if __name__ == '__main__':
   app.run(debug=True)