from flask import request, render_template, redirect, session
import pymongo
from datetime import datetime, timedelta

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["library_db"]
users = db["users"]
books = db["books"]
borrowed = db["borrowed"]

def setup_routes(app):
    @app.route('/')
    def home():
        return render_template("login.html")

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            uname = request.form['username']
            pword = request.form['password']
            user = users.find_one({"username": uname, "password": pword})
            if user:
                session['username'] = uname
                session['role'] = user['role']
                return redirect("/admin" if user["role"] == "admin" else "/user")
            return render_template("login.html", error="Invalid credentials")
        return render_template("login.html")

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            uname = request.form['username']
            pword = request.form['password']
            role = request.form['role']
            if users.find_one({"username": uname}):
                return render_template("signup.html", error="User already exists")
            users.insert_one({"username": uname, "password": pword, "role": role})
            return redirect("/login")
        return render_template("signup.html")

    @app.route('/admin')
    def admin_dashboard():
        if session.get("role") != "admin":
            return redirect("/")
        all_books = books.find()
        return render_template("admin_dashboard.html", books=all_books)

    @app.route('/admin/add', methods=['POST'])
    def add_book():
        if session.get("role") != "admin":
            return redirect("/")
        title = request.form['title']
        author = request.form['author']
        books.insert_one({"title": title, "author": author})
        return redirect("/admin")

    @app.route('/admin/delete/<title>')
    def delete_book(title):
        if session.get("role") != "admin":
            return redirect("/")
        books.delete_one({"title": title})
        return redirect("/admin")

    @app.route('/user')
    def user_dashboard():
        if session.get("role") != "user":
            return redirect("/")
        return render_template("user_dashboard.html")

    @app.route('/user/search')
    def search_books():
        q = request.args.get("q", "")
        results = books.find({"title": {"$regex": q, "$options": "i"}})
        return render_template("search_results.html", books=results, q=q)

    @app.route('/user/borrow/<title>', methods=['GET', 'POST'])
    def borrow_book(title):
        if session.get("role") != "user":
            return redirect("/")

        book = books.find_one({"title": title})
        if not book:
            return "Book not found", 404

        if request.method == 'POST':
            phone = request.form['phone']
            borrow_date = request.form['borrow_date']
            return_date = request.form['return_date']
            borrowed.insert_one({
                "username": session['username'],
                "title": title,
                "phone": phone,
                "borrow_date": borrow_date,
                "return_date": return_date
            })
            return redirect("/user/mybooks")

        borrow_date = datetime.today().date()
        return_date = borrow_date + timedelta(days=7)

        return render_template("borrow_form.html", book=book,
                            borrow_date=borrow_date.isoformat(),
                            return_date=return_date.isoformat())


    @app.route('/user/return/<title>')
    def return_book(title):
        if session.get("role") != "user":
            return redirect("/")
        borrowed.delete_one({"username": session['username'], "title": title})
        return redirect("/user")

    @app.route('/user/mybooks')
    def my_books():
        if session.get("role") != "user":
            return redirect("/")
        books_list = borrowed.find({"username": session['username']})
        return render_template("my_books.html", books=books_list)
    @app.route('/admin/update/<title>', methods=['GET', 'POST'])
    def update_book(title):
        if session.get("role") != "admin":
            return redirect("/")
        
        if request.method == 'POST':
            new_title = request.form['title']
            new_author = request.form['author']
            books.update_one({"title": title}, {"$set": {"title": new_title, "author": new_author}})
            return redirect("/admin")

        book = books.find_one({"title": title})
        return render_template("update_book.html", book=book)
    @app.route('/logout')
    def logout():
        session.clear()  # Clear session data
        return redirect('/login')  # Redirect to login page
