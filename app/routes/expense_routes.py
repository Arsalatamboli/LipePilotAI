from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from app.routes.main_routes import login_required
from app.models.expense_model import ExpenseModel

expense_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@expense_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_id = session['user_id']
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        expense_date = request.form.get('expense_date', today_str)
        category = request.form.get('category', 'Other')
        amount = float(request.form.get('amount', 0.0))
        description = request.form.get('description', '').strip()
        
        if amount <= 0:
            flash('Expense amount must be greater than 0.', 'warning')
        else:
            ExpenseModel.add_expense(user_id, expense_date, category, amount, description)
            flash(f'Expense of ₹{amount:.2f} under "{category}" logged successfully!', 'success')
            return redirect(url_for('expenses.index'))

    expenses = ExpenseModel.get_by_user(user_id, limit=50)
    category_summary = ExpenseModel.get_category_breakdown(user_id)
    monthly_summary = ExpenseModel.get_monthly_summary(user_id)
    
    total_spent = sum([float(c['total_amount']) for c in category_summary]) if category_summary else 0.0

    return render_template(
        'expenses/index.html',
        today_str=today_str,
        expenses=expenses,
        category_summary=category_summary,
        monthly_summary=monthly_summary,
        total_spent=total_spent
    )

@expense_bp.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete(expense_id):
    user_id = session['user_id']
    ExpenseModel.delete_expense(expense_id, user_id)
    flash('Expense entry deleted.', 'info')
    return redirect(url_for('expenses.index'))
