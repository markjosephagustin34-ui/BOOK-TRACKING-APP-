from flask import Flask, request, redirect
from datetime import date

app = Flask(__name__)


# ==========================================================
# 📱 APP CLASSES
# ==========================================================

class Book:
    def __init__(self, book_id, title, author, year):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.year = int(year)
        self.is_available = True

    def mark_as_borrowed(self): self.is_available = False

    def mark_as_returned(self): self.is_available = True


class Member:
    def __init__(self, member_id, name, email, phone):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.phone = phone


class Loan:
    def __init__(self, loan_id, book, member):
        self.loan_id = loan_id
        self.book = book
        self.member = member
        self.borrow_date = date.today()
        self.return_date = None

    @property
    def is_active(self): return self.return_date is None

    def complete_return(self): self.return_date = date.today()


books = []
members = []
loans = []

# ==========================================================
# 🎨 AMAZING CSS DESIGN
# ==========================================================

CSS = """
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding-bottom: 50px;
    }
    .navbar {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 100;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    .navbar .brand { color: white; font-size: 1.8rem; font-weight: 700; }
    .navbar a {
        color: white;
        text-decoration: none;
        margin-left: 20px;
        font-weight: 500;
        padding: 8px 20px;
        border-radius: 25px;
        transition: all 0.3s ease;
    }
    .navbar a:hover {
        background: white;
        color: #667eea;
    }
    .container { max-width: 1100px; margin: 40px auto; padding: 0 20px; }
    .card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        animation: slideUp 0.5s ease;
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    h1 { color: #333; margin-bottom: 20px; font-size: 2rem; }
    h3 { color: #555; margin-bottom: 15px; }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 25px;
        margin-bottom: 40px;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        color: white;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .stat-number { font-size: 4rem; font-weight: 700; }
    .stat-label { font-size: 1.2rem; opacity: 0.9; }
    .btn {
        display: inline-block;
        padding: 12px 30px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 30px;
        cursor: pointer;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.3s ease;
        font-size: 1rem;
    }
    .btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
    }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    input, select {
        padding: 15px;
        border: 2px solid #eee;
        border-radius: 12px;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #f9f9f9;
    }
    input:focus, select:focus {
        outline: none;
        border-color: #667eea;
        background: white;
    }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        padding: 15px;
        text-align: left;
        font-weight: 600;
    }
    td { padding: 15px; border-bottom: 1px solid #eee; }
    tr:hover { background: #f8f9ff; }
    .loan-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
    .btn-danger { background: linear-gradient(90deg, #e74c3c, #c0392b); }
    .status { padding: 5px 15px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; }
    .available { background: #d4edda; color: #155724; }
    .borrowed { background: #f8d7da; color: #721c24; }
</style>
"""


# ==========================================================
# 📄 HTML PAGES
# ==========================================================

def page(content):
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>📱 Book Tracker Pro</title>{CSS}</head>
    <body>
        <nav class="navbar">
            <div class="brand">📱 Book Tracker</div>
            <div>
                <a href="/">🏠 Home</a>
                <a href="/books">📚 Books</a>
                <a href="/members">👥 Members</a>
                <a href="/loans">📱 Loans</a>
            </div>
        </nav>
        <div class="container">{content}</div>
    </body>
    </html>
    """


HOME = """
<h1>📊 Dashboard</h1>
<div class="stats-grid">
    <div class="stat-card"><div class="stat-number">{0}</div><div class="stat-label">📚 Total Books</div></div>
    <div class="stat-card"><div class="stat-number">{1}</div><div class="stat-label">👥 Members</div></div>
    <div class="stat-card"><div class="stat-number">{2}</div><div class="stat-label">📱 Active Loans</div></div>
</div>
<div style="display: flex; gap: 15px; flex-wrap: wrap;">
    <a href="/books" class="btn">➕ Add Book</a>
    <a href="/members" class="btn">👤 Add Member</a>
    <a href="/loans" class="btn">📱 Track Loan</a>
</div>
"""

BOOKS = """
<h1>📚 Book Inventory</h1>
<div class="card"><h3>➕ Add New Book</h3>
    <form method="POST">
        <div class="form-grid">
            <input name="book_id" placeholder="Book ID (e.g. B001)" required>
            <input name="title" placeholder="Book Title" required>
            <input name="author" placeholder="Author Name" required>
            <input name="year" placeholder="Year" required>
        </div>
        <button class="btn" style="margin-top: 15px;">✨ Add Book</button>
    </form>
</div>
<div class="card"><h3>📖 All Books</h3>
    <table>
        <thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Year</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>{0}</tbody>
    </table>
</div>
"""

MEMBERS = """
<h1>👥 Members</h1>
<div class="card"><h3>👤 Register New Member</h3>
    <form method="POST">
        <div class="form-grid">
            <input name="member_id" placeholder="Member ID" required>
            <input name="name" placeholder="Full Name" required>
            <input name="email" placeholder="Email Address" required>
            <input name="phone" placeholder="Phone Number" required>
        </div>
        <button class="btn" style="margin-top: 15px;">✨ Register</button>
    </form>
</div>
<div class="card"><h3>All Members</h3>
    <table>
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th></tr></thead>
        <tbody>{0}</tbody>
    </table>
</div>
"""

LOANS = """
<h1>📱 Loan Tracker</h1>
<div class="loan-grid">
    <div class="card"><h3>📤 Borrow Book</h3>
        <form method="POST">
            <input type="hidden" name="action" value="borrow">
            <select name="book_id" required><option value="">Choose a book</option>{0}</select>
            <select name="member_id" required><option value="">Choose a member</option>{1}</select>
            <button class="btn" style="margin-top: 15px; width: 100%;">📤 Confirm Borrow</button>
        </form>
    </div>
    <div class="card"><h3>📥 Return Book</h3>
        <form method="POST">
            <input type="hidden" name="action" value="return">
            <select name="book_id" required><option value="">Choose a book to return</option>{2}</select>
            <button class="btn" style="margin-top: 15px; width: 100%;">📥 Confirm Return</button>
        </form>
    </div>
</div>
<div class="card"><h3>🔴 Active Loans</h3>
    <table>
        <thead><tr><th>Tracker ID</th><th>Book</th><th>Member</th><th>Date</th></tr></thead>
        <tbody>{3}</tbody>
    </table>
</div>
"""


# ==========================================================
# 🚀 ROUTES
# ==========================================================

@app.route('/')
def index():
    active = len([l for l in loans if l.is_active])
    return page(HOME.format(len(books), len(members), active))


@app.route('/books', methods=['GET', 'POST'])
def manage_books():
    if request.method == 'POST':
        books.append(Book(request.form['book_id'], request.form['title'],
                          request.form['author'], request.form['year']))
        return redirect('/books')

    rows = ''
    for b in books:
        status = f'<span class="status available">✅ Available</span>' if b.is_available else f'<span class="status borrowed">❌ Borrowed</span>'
        rows += f"<tr><td>{b.book_id}</td><td>{b.title}</td><td>{b.author}</td><td>{b.year}</td><td>{status}</td><td><a href='/delete_book/{b.book_id}' class='btn btn-danger'>🗑️</a></td></tr>"

    if not rows:
        rows = '<tr><td colspan="6" style="text-align:center;">No books yet</td></tr>'

    return page(BOOKS.format(rows))


@app.route('/delete_book/<bid>')
def delete_book(bid):
    global books
    books = [b for b in books if b.book_id != bid]
    return redirect('/books')


@app.route('/members', methods=['GET', 'POST'])
def manage_members():
    if request.method == 'POST':
        members.append(Member(request.form['member_id'], request.form['name'],
                              request.form['email'], request.form['phone']))
        return redirect('/members')

    rows = ''
    for m in members:
        rows += f"<tr><td>{m.member_id}</td><td>{m.name}</td><td>{m.email}</td><td>{m.phone}</td></tr>"

    if not rows:
        rows = '<tr><td colspan="4" style="text-align:center;">No members yet</td></tr>'

    return page(MEMBERS.format(rows))


@app.route('/loans', methods=['GET', 'POST'])
def manage_loans():
    if request.method == 'POST':
        if request.form['action'] == 'borrow':
            b = next((x for x in books if x.book_id == request.form['book_id']), None)
            m = next((x for x in members if x.member_id == request.form['member_id']), None)
            if b and b.is_available and m:
                loans.append(Loan(f"TRK{len(loans) + 1:03d}", b, m))
                b.mark_as_borrowed()
        else:
            b = next((x for x in books if x.book_id == request.form['book_id']), None)
            l = next((x for x in loans if x.book.book_id == request.form['book_id'] and x.is_active), None)
            if l and b:
                l.complete_return()
                b.mark_as_returned()
        return redirect('/loans')

    active = [l for l in loans if l.is_active]

    book_opts = ''.join(f"<option value='{b.book_id}'>{b.title}</option>" for b in books if b.is_available)
    mem_opts = ''.join(f"<option value='{m.member_id}'>{m.name}</option>" for m in members)
    loan_opts = ''.join(f"<option value='{l.book.book_id}'>{l.book.title}</option>" for l in active)

    rows = ''
    for l in active:
        rows += f"<tr><td>{l.loan_id}</td><td>{l.book.title}</td><td>{l.member.name}</td><td>{l.borrow_date}</td></tr>"

    if not rows:
        rows = '<tr><td colspan="4" style="text-align:center;">No active loans</td></tr>'

    return page(LOANS.format(book_opts, mem_opts, loan_opts, rows))


# ==========================================================
# ▶️ RUN
# ==========================================================

if __name__ == '__main__':
    app.run(debug=True)