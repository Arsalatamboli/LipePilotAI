from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.main_routes import login_required
from app.models.user_model import UserModel

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_id = session['user_id']
    user = UserModel.get_by_id(user_id)

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_info':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            
            if username and email:
                UserModel.update_profile(user_id, username, email)
                session['username'] = username
                session['email'] = email
                flash('Profile details updated successfully.', 'success')
            else:
                flash('Username and email cannot be empty.', 'warning')
                
        elif action == 'update_password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            full_user = UserModel.get_by_email(session['email'])
            if not UserModel.verify_password(full_user['password_hash'], current_password):
                flash('Current password is incorrect.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'warning')
            else:
                UserModel.update_password(user_id, new_password)
                flash('Password updated successfully!', 'success')
                
        return redirect(url_for('profile.index'))

    return render_template('profile/index.html', user=user)
