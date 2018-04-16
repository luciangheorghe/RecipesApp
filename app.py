from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
# from data import Recipes
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Camelia_2000'
app.config['MYSQL_DB'] = 'myrecipesapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

# Recipes = Recipes()

# Home
@app.route('/')
def home():
    return render_template('home.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Recipes
@app.route('/recipes')
def recipes():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get recipes
    result = cur.execute("SELECT * FROM recipes")

    recipes = cur.fetchall()

    if result > 0:
        return render_template('recipes.html', recipes=recipes)
    else:
        msg = 'NO Recipes Found'
        return render_template('recipes.html', msg=msg)
    # Close connection
    cur.close()

# Single Recipe
@app.route('/recipe/<string:id>/')
def recipe(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get recipe
    result = cur.execute("SELECT * FROM recipes WHERE recipe_ID = %s", [id])

    recipe = cur.fetchone()

    return render_template('recipe.html', recipe=recipe)

#Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by Username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get recipes
    result = cur.execute("SELECT * FROM recipes")

    recipes = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', recipes=recipes)
    else:
        msg = 'NO Recipes Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()


# Recipe Form Class
class RecipeForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    chef = StringField('Chef', [validators.Length(min=4, max=100)])
    level = StringField('Level', [validators.Length(min=4, max=100)])
    servings = IntegerField('Servings')
    reviews = IntegerField('Reviews')
    total = IntegerField('Total')

# Add Recipe
@app.route('/add_recipe', methods=['GET', 'POST'])
@is_logged_in
def add_recipe():
    form = RecipeForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        chef = form.chef.data
        level = form.level.data
        servings = form.servings.data
        reviews = form.reviews.data
        total = form.total.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO recipes(title, chef, level, servings, reviews) VALUES(%s, %s, %s, %s, %s)", (title, chef, level, servings, reviews))

        # Commit
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Recipe Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_recipe.html', form=form)

def add_tiempo():
    form = RecipeForm(request.form)
    if request.method == 'POST' and form.validate():

        total = form.total.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO tiempo(total) VALUES(%s)", (total))

        # Commit
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Recipe Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_recipe.html', form=form)



if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
