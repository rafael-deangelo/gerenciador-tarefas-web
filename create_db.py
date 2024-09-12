from app import db, Task, app

# Criar o contexto da aplicação
with app.app_context():
    tasks = Task.query.all()
    for task in tasks:
        print(task.status)
