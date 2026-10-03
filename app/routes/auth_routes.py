from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user_model import UserModel

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'warning')
            return render_template('auth/login.html')
            
        user = UserModel.get_by_email(email)
        if user and UserModel.verify_password(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not email or not password:
            flash('All fields are required.', 'warning')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('auth/register.html')
            
        # Check existing email/username
        if UserModel.get_by_email(email):
            flash('An account with this email already exists.', 'danger')
            return render_template('auth/register.html')
            
        if UserModel.get_by_username(username):
            flash('Username is already taken.', 'danger')
            return render_template('auth/register.html')
            
        # Create user with secure password hash
        user_id = UserModel.create_user(username, email, password)
        session['user_id'] = user_id
        session['username'] = username
        session['email'] = email
        flash('Account registered successfully! Welcome to LifePilot AI.', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
