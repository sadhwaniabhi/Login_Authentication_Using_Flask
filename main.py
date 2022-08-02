from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

# --------- database configuration
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------ login manager configuration
login_manager = LoginManager()
login_manager.init_app(app)


# ----CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


# Line below only required once, when creating DB.
# db.create_all()


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    """function to register user and save their data to database using the request method of flask"""
    if request.method == "POST":

        if User.query.filter_by(email=request.form.get("email")).first():
            flash("User already exist! Please login.")
            return redirect(url_for("login"))

        new_user = User(email=request.form.get("email"),
                        password=generate_password_hash(password=request.form.get("password"), method='pbkdf2:sha256',
                                                        salt_length=8),
                        name=request.form.get("name")
                        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("secrets"))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password_ = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User does not exist!")
            return redirect(url_for("login"))

        else:

            if check_password_hash(user.password, password_):
                login_user(user)
                return redirect(url_for("secrets"))

            else:
                flash("Password is incorrect! Please try again.")
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/download')
@login_required
def download():
    """function to let user download the cheat sheet file"""
    return send_from_directory(directory='static', path='files/cheat_sheet.pdf')


# filename parameter has been renamed to path


if __name__ == "__main__":
    app.run(debug=True)
