# app/web/app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from app.db.connection import Database
import bcrypt
from app.web.routes_employee import employee_bp 

# -------------------
# Flask setup
# -------------------
app = Flask(__name__)
app.secret_key = "super_secret_for_sessions"  # potrzebne do sesji

app.register_blueprint(employee_bp, url_prefix="/employees")

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# -------------------
# User model dla Flask-Login
# -------------------
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# -------------------
# Load user callback
# -------------------
@login_manager.user_loader
def load_user(user_id):
    db = Database()
    cur = db.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return User(row['id'], row['username'], row['password'])
    return None

# -------------------
# Routes
# -------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode('utf-8')

        db = Database()
        cur = db.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        cur.close()

        if row and bcrypt.checkpw(password, row['password'].encode('utf-8')):
            user = User(row['id'], row['username'], row['password'])
            login_user(user)
            return redirect(url_for("main"))
        else:
            flash("Niepoprawny login lub hasło")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/main")
@login_required
def main():
    return render_template("main.html", user=current_user.username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# -------------------
# Blueprint pracowników
# -------------------
try:
    from app.web.routes_employee import employee_bp
#    app.register_blueprint(employee_bp, url_prefix="/employees")
except ModuleNotFoundError:
    print("Blueprint pracowników nie istnieje, pomijam rejestrację")

# -------------------
# Run server
# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5566, debug=True)
