from sqlite3 import IntegrityError

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '12332'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pendente')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifica se o usuário já existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('O nome de usuário já existe. Por favor escolha um diferente!', 'danger')
            return redirect(url_for('register'))

        # Se não existir, criar um novo usuário
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Por favor faça login!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/all_tasks')
def all_tasks():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    tasks = Task.query.all()  # Recupera todas as tarefas de todos os usuários
    return render_template('all_tasks.html', tasks=tasks)


@app.route('/change_task_owner/<int:task_id>', methods=['GET', 'POST'])
def change_task_owner(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = Task.query.get_or_404(task_id)

    # Apenas para garantir que o usuário esteja autenticado
    if request.method == 'POST':
        new_user_id = request.form['new_user_id']
        new_user = User.query.get(new_user_id)
        if new_user:
            task.user_id = new_user.id
            db.session.commit()
            flash('Task owner changed successfully!', 'success')
            return redirect(url_for('all_tasks'))
        else:
            flash('User not found.', 'danger')

    users = User.query.all()
    return render_template('change_task_owner.html', task=task, users=users)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    status_filter = request.args.get('status')

    # Se houver um filtro de status, aplicar a filtragem
    if status_filter:
        tasks = Task.query.filter_by(user_id=user.id, status=status_filter).all()
    else:
        tasks = Task.query.filter_by(user_id=user.id).all()

    return render_template('dashboard.html', tasks=tasks, username=user.username)



@app.route('/task_form', methods=['GET', 'POST'])
def task_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        user_id = session['user_id']
        new_task = Task(title=title, description=description, status=status, user_id=user_id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('task_form.html')

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.status = request.form['status']
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('task_form.html', task=task)

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
