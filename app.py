from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_task_colaboration'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

#  Definisi model User untuk tabel 'users'
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        """Method untuk menyimpan password yang telah di-hash ke dalam database."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Method untuk memeriksa apakah password yang dimasukkan sesuai."""
        return check_password_hash(self.password_hash, password)
    
    task_lists = relationship("TaskLists", back_populates="user")

# Definisi model TaskLists untuk tabel 'task_lists'
class TaskLists(db.Model):
    __tablename__ = 'task_lists'  
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)

    user = relationship("Users", back_populates="task_lists")
    
    def set_password(self, password):
        """Method untuk menyimpan password ruangan yang telah di-hash ke dalam database."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Method untuk memeriksa apakah password ruangan yang dimasukkan sesuai."""
        return check_password_hash(self.password_hash, password)

# Definisi model Collaborations untuk tabel 'collaborations'
class Collaborations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_list_id = db.Column(db.Integer, db.ForeignKey('task_lists.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

# Definisi model Tasks untuk tabel 'tasks'
class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_list_id = db.Column(db.Integer, db.ForeignKey('task_lists.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, nullable=False, default=False)

# Konfigurasi untuk mengelola user session dan authentication
@login_manager.user_loader
def load_user(user_id):
    """Fungsi untuk mengambil data user berdasarkan ID."""
    return Users.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    """Fungsi untuk menangani akses tanpa login."""
    return redirect(url_for('login'))

# Route untuk login
@app.route('/login', methods=["GET","POST"])
def login():
    """Route untuk halaman login."""
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Jika login berhasil, user akan diarahkan ke halaman utama
            login_user(user)
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            # Jika login gagal, user akan tetap di halaman login dengan pesan kesalahan
            return redirect(url_for('login', error="Invalid Credential"))
    return render_template('auth/login.html')

# Route untuk register
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Route untuk halaman register."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            # Jika username sudah digunakan, user akan tetap di halaman register dengan pesan kesalahan
            return redirect(url_for('register', error="Username already exists"))

        # Jika registrasi berhasil, user akan diarahkan ke halaman utama
        new_user = Users(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        session['user_id'] = new_user.id
        return redirect(url_for('index'))
    return render_template('auth/register.html')

# Route untuk logout
@app.route('/logout')
@login_required
def logout():
    """Route untuk logout."""
    logout_user()
    return redirect(url_for('login'))

# Route untuk halaman utama
@app.route('/')
@login_required
def index():
    """Route untuk halaman utama."""
    user_id = current_user.id
    task_lists = TaskLists.query.filter_by(user_id=user_id).all()
    return render_template('index.html', task_lists=task_lists)

# Route untuk halaman profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Route untuk halaman profile."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            # Jika password tidak sesuai, user akan tetap di halaman profile dengan pesan kesalahan
            return render_template('profile.html', error="Passwords do not match")

        # Update data user dan komit ke database
        current_user.username = username
        current_user.email = email
        if password:
            current_user.set_password(password)
        db.session.commit()
        return redirect(url_for('index'))

    # Mengambil data username dan email user yang sedang login
    username = current_user.username
    email = current_user.email
    return render_template('profile.html', username=current_user.username, email=current_user.email)


@app.route('/search', methods=['GET'])
@login_required
def search():
    # Ambil kata kunci pencarian dari query string
    keyword = request.args.get('keyword', '')

    # Cari tasklists berdasarkan judulnya
    task_lists = TaskLists.query.filter(TaskLists.title.ilike(f'%{keyword}%')).all()

    # Buat kamus kosong untuk menyimpan informasi username yang membuat setiap tasklist
    tasklist_creators = {}

    # Loop melalui setiap tasklist yang ditemukan
    for task_list in task_lists:
        # Dapatkan user yang membuat tasklist menggunakan user_id
        creator = Users.query.get(task_list.user_id)
        # Tambahkan informasi username ke kamus menggunakan id tasklist sebagai kunci
        tasklist_creators[task_list.id] = creator.username

    # Kembalikan hasil pencarian dan informasi username ke template
    return render_template('search_results.html', task_lists=task_lists, keyword=keyword, tasklist_creators=tasklist_creators)

# Route untuk membuat room
@app.route('/create_room', methods=["POST"])
@login_required
def create_room():
    """Route untuk membuat ruangan baru."""
    if request.method == "POST":
        title = request.form['title']
        user_id = current_user.id  # Ambil user_id dari current_user
        password_hash = request.form['password']

        # Periksa apakah password kosong
        if not password_hash:
            password_hash = None

        # Buat objek room baru, simpan ke database, dan arahkan kembali ke halaman utama
        new_room = TaskLists(title=title, user_id=user_id)
        new_room.set_password(password_hash)
        db.session.add(new_room)
        db.session.commit()
        return redirect(url_for('index'))


# Route untuk bergabung ke room
@app.route('/collaborate/<int:task_list_id>', methods=['GET', 'POST'])
@login_required
def collaborate(task_list_id):
    """Route untuk bergabung ke ruangan."""
    # Ambil tasklist dari database
    task_list = TaskLists.query.get(task_list_id)

    # Cek apakah pengguna adalah pemilik tasklist
    if task_list.user_id == current_user.id:
        return redirect(url_for('todo_list', task_list_id=task_list_id))

    if request.method == 'POST':
        # Ambil password dari form
        password = request.form['password']
        
        # Jika tasklist tidak memiliki password atau password sesuai, tambahkan kolaborator
        if not task_list.password_hash or check_password_hash(task_list.password_hash, password):
            # Cek apakah kolaborator sudah ada
            if Collaborations.query.filter_by(task_list_id=task_list_id, user_id=current_user.id).first():
                return redirect(url_for('todo_list', task_list_id=task_list_id))
            
            # Tambahkan kolaborator baru ke tasklist
            collaboration = Collaborations(task_list_id=task_list_id, user_id=current_user.id)
            db.session.add(collaboration)
            db.session.commit()
            return redirect(url_for('todo_list', task_list_id=task_list_id))
            
        else:
            # Jika password tidak sesuai, maka kembalikan pengguna ke halaman kolaborasi
            return redirect(url_for('collaborate', task_list_id=task_list_id))
    
    # Jika tidak ada metode POST (misalnya pengguna mengakses halaman secara langsung), dan tasklist tidak memiliki password, maka tambahkan pengguna sebagai kolaborator
    if not task_list.password_hash:
        # Cek apakah kolaborator sudah ada
        if Collaborations.query.filter_by(task_list_id=task_list_id, user_id=current_user.id).first():
            return redirect(url_for('todo_list', task_list_id=task_list_id))
        
        # Tambahkan kolaborator baru ke tasklist
        collaboration = Collaborations(task_list_id=task_list_id, user_id=current_user.id)
        db.session.add(collaboration)
        db.session.commit()
        return redirect(url_for('todo_list', task_list_id=task_list_id))

    # Render halaman kolaborasi login jika pengguna harus memasukkan password
    return render_template('collaborate_login.html', task_list=task_list)

# Route untuk menambahkan task baru ke dalam todo list
@app.route('/add_task/<int:task_list_id>', methods=["POST"])
@login_required
def add_task(task_list_id):
    """Route untuk menambahkan task baru ke dalam todo list."""
    if request.method == "POST":
        description = request.form['description']
        due_date = request.form['due_date']

        # Buat objek task baru, simpan ke database, dan arahkan kembali ke halaman todo list
        new_task = Tasks(task_list_id=task_list_id, description=description, due_date=due_date)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('todo_list', task_list_id=task_list_id))

# Route untuk menandai task sebagai selesai
@app.route('/complete_task/<int:task_id>', methods=["POST"])
@login_required
def complete_task(task_id):
    """Route untuk menandai task sebagai selesai."""
    task = Tasks.query.get(task_id)
    if task:
        task.completed = True
        db.session.commit()
    return redirect(url_for('todo_list', task_list_id=task.task_list_id))

# Route untuk menghapus task dari todo list
@app.route('/delete_task/<int:task_id>', methods=["GET", "POST"])
@login_required
def delete_task(task_id):
    """Route untuk menghapus task dari todo list."""
    task = Tasks.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('todo_list', task_list_id=task.task_list_id))


# Route untuk halaman todo list task
@app.route('/todo_list/<int:task_list_id>')
@login_required
def todo_list(task_list_id):
    """Route untuk halaman todo list task."""
    task_list = TaskLists.query.get(task_list_id)
    if task_list:
        tasks = Tasks.query.filter_by(task_list_id=task_list_id).all()
        return render_template('collaborate.html', task_list=task_list, tasks=tasks)
    else:
        # Tampilkan pesan error jika todo list tidak ditemukan
        return "Todo List not found", 404



if __name__ == '__main__':
    app.run(debug=True)
