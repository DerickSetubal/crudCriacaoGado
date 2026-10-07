from flask import Blueprint, render_template, request, redirect, url_for, flash, session

bp_auth = Blueprint('auth', __name__)

USUARIO_CORRETO = 'admin.neto'
SENHA_CORRETA = 'admin123'

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    """Tela de login de acesso único e restrito ao sistema."""
    # Se já estiver autenticado, redireciona para a dashboard
    if session.get('autenticado'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '').strip()

        if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
            session['autenticado'] = True
            session['usuario'] = usuario
            session.permanent = True  # Mantém a sessão
            flash('Login realizado com sucesso! Bem-vindo ao AgroGestão.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Usuário ou senha incorretos. Acesso restrito.', 'danger')

    return render_template('login.html')


@bp_auth.route('/logout')
def logout():
    """Encerra a sessão e retorna à tela de login."""
    session.clear()
    flash('Você saiu do sistema com segurança.', 'info')
    return redirect(url_for('auth.login'))

