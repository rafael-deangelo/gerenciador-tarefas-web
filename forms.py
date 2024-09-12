from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
from models import User


class TaskForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    status = SelectField('Status', choices=[('pendente', 'Pendente'), ('em andamento', 'Em Andamento'),
                                            ('concluída', 'Concluída')], validators=[DataRequired()])

    # Adicionar o campo para selecionar um usuário
    user_id = SelectField('Atribuir a', coerce=int)

    submit = SubmitField('Salvar')

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # Preenche a lista de usuários no campo de atribuição de tarefa
        self.user_id.choices = [(user.id, user.username) for user in User.query.all()]
