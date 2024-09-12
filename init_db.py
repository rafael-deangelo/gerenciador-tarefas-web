from app import db, app

# Criar o contexto da aplicação
with app.app_context():
    # Apagar todas as tabelas existentes (se houver)
    db.drop_all()
    # Criar as tabelas novas de acordo com os modelos definidos
    db.create_all()
    print("Banco de Dados inicializado e Tabelas Criadas!")
