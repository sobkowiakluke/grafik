from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import bcrypt
from app.db.connection import Database

app = Flask(__name__)
app.secret_key = "supersecretkey"  # wymagane dla sesji Flask-Login

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db = Database()

# Minimalny User
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    cur = db.cursor()
    cur.execute("SELECT id, username FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return User(row["id"], row["username"])
    return None

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        cur = db.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        cur.close()

        if row and bcrypt.checkpw(password, row["password"].encode("utf-8")):
            user = User(row["id"], row["username"])
            login_user(user)
            return redirect(url_for("main"))
        else:
            return render_template("login.html", error="Nieprawidłowy login lub hasło")

    return render_template("login.html")

@app.route("/main")
@login_required
def main():
    return render_template("main.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5566, debug=True)
