# ============================================================================
# main.py — Flask Authentication Application
# ============================================================================
# This is the main entry point of the Flask web application. It sets up:
#   - A Flask web server with secret key configuration
#   - A SQLite database via SQLAlchemy to store user credentials
#   - User authentication (register, login, logout) via Flask-Login
#   - Protected routes that require a logged-in session
#   - A file download endpoint for authenticated users
# ============================================================================

# --- Import Section -----------------------------------------------------------

# Flask: the core web framework class that creates the application instance.
# render_template: renders Jinja2 HTML templates from the 'templates/' folder.
# request: provides access to incoming HTTP request data (form fields, method, etc.).
# url_for: generates URLs for Flask route functions by their endpoint name.
# redirect: returns an HTTP redirect response to send the user to a different URL.
# flash: stores a one-time message in the session to display feedback to the user.
# send_from_directory: securely serves a file from a given directory on the server.
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory

# generate_password_hash: creates a salted hash of a plaintext password for secure storage.
# check_password_hash: verifies a plaintext password against its previously generated hash.
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy: the ORM (Object-Relational Mapper) extension for Flask that simplifies
# database interactions by mapping Python classes to database tables.
from flask_sqlalchemy import SQLAlchemy

# DeclarativeBase: the modern SQLAlchemy 2.0 base class for declaring ORM models.
# Mapped: a type annotation helper that tells SQLAlchemy a class attribute is a mapped column.
# mapped_column: defines a column on an ORM model with its type and constraints.
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Integer, String: SQLAlchemy column type objects used to specify the data type of each column.
from sqlalchemy import Integer, String

# UserMixin: a convenience mixin from Flask-Login that provides default implementations
#   for is_authenticated, is_active, is_anonymous, and get_id().
# login_user: logs a user in by writing their ID into the session cookie.
# LoginManager: the central object that coordinates Flask-Login's session management.
# login_required: a decorator that restricts a route to authenticated users only.
# current_user: a proxy object that always points to the currently logged-in user
#   (or an anonymous user if nobody is logged in).
# logout_user: logs the current user out by clearing their session data.
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user


# --- Application Initialization -----------------------------------------------

# Create the Flask application instance.
# __name__ tells Flask where to look for templates, static files, etc.
app = Flask(__name__)

# SECRET_KEY is used by Flask to cryptographically sign session cookies and flash messages.
# In production, this should be a long, random, and secret string stored in environment variables.
app.config['SECRET_KEY'] = 'secret-key-goes-here'


# --- Database Configuration ---------------------------------------------------

# Define a custom base class for all SQLAlchemy ORM models.
# SQLAlchemy 2.0 requires models to inherit from a DeclarativeBase subclass.
class Base(DeclarativeBase):
    pass  # No additional configuration needed; this simply establishes the base.


# Configure the database URI to use a local SQLite file named 'users.db'.
# The 'sqlite:///' prefix tells SQLAlchemy to use the SQLite engine.
# The file will be created inside the 'instance/' folder (Flask default for instance-relative paths).
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Instantiate the SQLAlchemy object with our custom Base class.
# This binds the ORM engine to our declarative base so models can be auto-discovered.
db = SQLAlchemy(model_class=Base)

# Initialize the SQLAlchemy extension with the Flask app.
# This connects the db object to the app's configuration (database URI, etc.).
db.init_app(app)


# --- Flask-Login Setup ---------------------------------------------------------

# Create a LoginManager instance, which manages user session state.
login_manager = LoginManager()

# Bind the LoginManager to the Flask app so it can access the app's session and config.
login_manager.init_app(app)


# The user_loader callback tells Flask-Login how to reload a user object from the
# user ID stored in the session cookie. It is called on every request to restore
# the current_user proxy.
@login_manager.user_loader
def load_user(user_id):
    # db.get_or_404() fetches the User by primary key; if not found, it aborts with 404.
    return db.get_or_404(User, user_id)


# --- Database Model -----------------------------------------------------------

# The User model maps to a database table named 'user' (lowercase by default).
# It inherits from:
#   - UserMixin: provides default Flask-Login interface methods.
#   - db.Model: makes it a SQLAlchemy ORM model bound to our database.
class User(UserMixin, db.Model):
    # 'id' column: integer primary key that auto-increments for each new user.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # 'email' column: stores the user's email address (up to 100 characters).
    # unique=True ensures no two users can register with the same email.
    email: Mapped[str] = mapped_column(String(100), unique=True)

    # 'password' column: stores the hashed password string (up to 100 characters).
    # The actual plaintext password is never stored — only its salted hash.
    password: Mapped[str] = mapped_column(String(100))

    # 'name' column: stores the user's display name (up to 1000 characters).
    name: Mapped[str] = mapped_column(String(1000))


# --- Create Database Tables ---------------------------------------------------

# app.app_context() pushes an application context so that SQLAlchemy knows which
# app (and therefore which database) to use when creating tables.
with app.app_context():
    # db.create_all() inspects all model classes that inherit from Base and creates
    # any tables that do not already exist in the database.  Existing tables are not modified.
    db.create_all()


# --- Route: Home Page ----------------------------------------------------------

# The root URL ('/') serves the landing page of the application.
@app.route('/')
def home():
    # Render 'index.html' and pass the logged_in flag so the template can conditionally
    # show or hide the Login/Register buttons for authenticated users.
    return render_template("index.html", logged_in=current_user.is_authenticated)


# --- Route: User Registration --------------------------------------------------

# The '/register' route handles both:
#   GET  — display the registration form.
#   POST — process the submitted registration form.
@app.route('/register', methods=["GET", "POST"])
def register():
    # Check if the form was submitted (POST request).
    if request.method == "POST":

        # Retrieve the email value from the submitted form data.
        email = request.form.get('email')

        # Query the database to check if a user with this email already exists.
        # db.select(User) constructs a SELECT query on the User table.
        # .where(User.email == email) filters rows where the email column matches.
        result = db.session.execute(db.select(User).where(User.email == email))

        # .scalar() returns the first column of the first row, or None if no rows matched.
        # Since email is unique, there will be at most one result.
        user = result.scalar()

        if user:
            # If a user with this email was found, inform them via a flash message
            # and redirect to the login page instead of creating a duplicate account.
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        # Hash the plaintext password using PBKDF2 with SHA-256 and a salt of 8 bytes.
        # This produces a secure hash string that can be safely stored in the database.
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),  # The plaintext password from the form.
            method='pbkdf2:sha256',        # The hashing algorithm to use.
            salt_length=8                  # Number of random bytes added as salt.
        )

        # Create a new User instance with the form data and the hashed password.
        new_user = User(
            email=request.form.get('email'),       # The user's email address.
            password=hash_and_salted_password,      # The securely hashed password.
            name=request.form.get('name'),          # The user's display name.
        )

        # Add the new user record to the current database session (staged for commit).
        db.session.add(new_user)

        # Commit the session to persist the new user record into the SQLite database.
        db.session.commit()

        # Automatically log in the newly registered user so they don't have to
        # go through the login page again.
        login_user(new_user)

        # Redirect to the secrets page (the protected content area).
        return redirect(url_for("secrets"))

    # If the request method is GET, simply render the registration form.
    # Pass logged_in to control navigation visibility in the template.
    return render_template("register.html", logged_in=current_user.is_authenticated)


# --- Route: User Login ----------------------------------------------------------

# The '/login' route handles both:
#   GET  — display the login form.
#   POST — authenticate the user with email and password.
@app.route('/login', methods=["GET", "POST"])
def login():
    # Check if the form was submitted (POST request).
    if request.method == "POST":
        # Retrieve the email and password from the submitted form data.
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the database for a user matching the submitted email.
        result = db.session.execute(db.select(User).where(User.email == email))

        # Extract the user object (or None if no match was found).
        user = result.scalar()

        # --- Validation: Check if the email exists in the database ---
        if not user:
            # No account found with this email — flash an error and reload the login page.
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))

        # --- Validation: Check if the provided password matches the stored hash ---
        elif not check_password_hash(user.password, password):
            # The password hash does not match — flash an error and reload the login page.
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))

        else:
            # Both email and password are valid — log the user in.
            login_user(user)

            # Redirect to the protected secrets page.
            return redirect(url_for('secrets'))

    # If the request method is GET, render the login form.
    return render_template("login.html", logged_in=current_user.is_authenticated)


# --- Route: Secrets Page (Protected) -------------------------------------------

# The '/secrets' route is protected by @login_required.
# If an unauthenticated user tries to access it, Flask-Login will redirect them
# to the login page (or return a 401 Unauthorized, depending on configuration).
@app.route('/secrets')
@login_required  # This decorator ensures only logged-in users can access this route.
def secrets():
    # Print the logged-in user's name to the server console (useful for debugging).
    print(current_user.name)

    # Render the secrets page, passing the user's name for a personalized greeting.
    # logged_in=True is hardcoded here because this route is only accessible when logged in.
    return render_template("secrets.html", name=current_user.name, logged_in=True)


# --- Route: Logout -------------------------------------------------------------

# The '/logout' route logs the current user out and redirects to the home page.
@app.route('/logout')
@login_required  # Only logged-in users can log out (prevents errors for anonymous users).
def logout():
    # Clear the user's session data, effectively logging them out.
    logout_user()

    # Redirect to the home page after logging out.
    return redirect(url_for('home'))


# --- Route: File Download (Protected) ------------------------------------------

# The '/download' route serves a file from the server's static directory.
# Only authenticated users can access this download.
@app.route('/download')
@login_required  # Restrict file downloads to logged-in users only.
def download():
    # send_from_directory() securely sends a file from the specified directory.
    # First argument: the directory to serve from ('static' folder in the project root).
    # path argument: the relative path to the file within that directory.
    # This prevents directory traversal attacks by validating the path.
    return send_from_directory('static', path="files/cheat_sheet.pdf")


# --- Application Entry Point ---------------------------------------------------

# This block runs only when the script is executed directly (not when imported as a module).
if __name__ == "__main__":
    # Start the Flask development server with debug mode enabled.
    # Debug mode provides:
    #   - Automatic server restart on code changes (hot reload).
    #   - An interactive debugger in the browser when errors occur.
    # WARNING: Never use debug=True in production — it exposes sensitive information.
    app.run(debug=True)
