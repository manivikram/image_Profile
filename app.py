from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import os
import mysql.connector
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired



class UploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    image = FileField('Image', validators=[FileRequired()])
    submit = SubmitField('Upload')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Set up database connection
db = mysql.connector.connect(
  host="localhost",
  user="admin",
  password="3210456",
  database="client_img_project"
)

# Set up login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return None
        user = User(user[0], user[1], user[2])
        return user


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Set up upload form
class UploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    image = FileField('Image', validators=[FileRequired()])
    submit = SubmitField('Upload')


# Set up login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


# Set up registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# Set up routes
# ...
import os

# @app.route('/', methods=['GET', 'POST'])
# @login_required
# def home():
#     cursor = db.cursor()
#     cursor.execute("SELECT * FROM images WHERE user_id = %s", (current_user.id,))
#     images = cursor.fetchall()

#     image_data_list = []
#     for image in images:
#         image_data = {
#             'id': image[0],
#             'title': image[2],
#             'width': image[3],
#             'height': image[4],
#             'format': image[5],
#             'filename': f'./static/uploads/{image[6]}'  # Assuming the filename is stored in the second column of the images table
#         }
#         image_data_list.append(image_data)

#     return render_template('home.html', image_data_list=image_data_list)
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM images WHERE user_id = %s", (current_user.id,))
    images = cursor.fetchall()

    image_data_list = []
    for image in images:
        filename = str(image[6])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            image_data = {
                'id': image[0],
                'title': image[2],
                'width': image[3],
                'height': image[4],
                'format': image[5],
                'filename': filename,
                'filepath': filepath
            }
            image_data_list.append(image_data)
        else:
            print(f"File '{filepath}' not found!")
    return render_template('home.html', image_data_list=image_data_list)


# @app.route('/', methods=['GET', 'POST'])
# @login_required
# def home():
#     cursor = db.cursor()
#     cursor.execute("SELECT * FROM images WHERE user_id = %s", (current_user.id,))
#     images = cursor.fetchall()

#     image_data_list = []
#     for image in images:
#         image_data = {
#             'id': image[0],
#             'title': image[2],
#             'width': image[3],
#             'height': image[4],
#             'format': image[5]
#         }
#         filename = str(image[6])
#         filepath = os.path.join(app.static_folder, 'upload', filename)

#         if os.path.exists(filepath):
#             image_data['filepath'] = os.path.join('upload', filename)
#             image_data_list.append(image_data)
#         else:
#             print(f"File '{filepath}' not found!")

#     return render_template('home.html', image_data_list=image_data_list,filename=filename)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], form.password.data):
            user = User(user[0], user[1], user[2])
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.before_request
def make_session_permanent():
    session.permanent = True
app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and  filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
   



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        user = cursor.fetchone()
        if user:
            flash('Username already exists')
        else:
            password_hash = generate_password_hash(form.password.data)
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (form.username.data, password_hash))
            db.commit()
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        # Save image to static/uploads folder
        image_file = form.image.data
        title = form.title.data
        extension = os.path.splitext(image_file.filename)[1]
        filename = secure_filename(title) + extension
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

        # Extract metadata from image
        with Image.open(image_path) as image:
            width, height = image.size
            format = image.format

        # Save metadata to database
        image_data = {
            'user_id': current_user.id,
            'title': title,
            'width': width,
            'height': height,
            'format': format,
            'filename': filename
        }
        cursor = db.cursor()
        cursor.execute("INSERT INTO images (user_id, title, width, height, format, filename) VALUES (%s, %s, %s, %s, %s, %s)", (current_user.id, title, width, height, format, filename))
        db.commit()

        flash('Image uploaded successfully')
        return redirect(url_for('home'))

    return render_template('upload.html', form=form)



app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM images WHERE id = %s AND user_id = %s", (id, current_user.id))
    image = cursor.fetchone()
    if not image:
        abort(404)
    filename = image[6]
    cursor.execute("DELETE FROM images WHERE id = %s", (id,))
    db.commit()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    flash('Image deleted successfully')
    return redirect(url_for('home'))


# Set up error handling
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
