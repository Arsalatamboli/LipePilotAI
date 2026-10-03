from app.db import execute_query

class ExpenseModel:
    @staticmethod
    def add_expense(user_id, expense_date, category, amount, description=''):
        """Adds a new expense entry."""
        sql = """
        INSERT INTO expenses (user_id, expense_date, category, amount, description)
        VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(sql, (user_id, expense_date, category, amount, description), commit=True)

    @staticmethod
    def get_by_user(user_id, limit=50):
        """Fetches expenses for a user sorted by date descending."""
        sql = "SELECT * FROM expenses WHERE user_id = %s ORDER BY expense_date DESC LIMIT %s"
        return execute_query(sql, (user_id, limit), fetch_all=True)

    @staticmethod
    def delete_expense(expense_id, user_id):
        """Deletes an expense record."""
        sql = "DELETE FROM expenses WHERE id = %s AND user_id = %s"
        execute_query(sql, (expense_id, user_id), commit=True)

    @staticmethod
    def get_category_breakdown(user_id):
        """Fetches sum of expenses grouped by category."""
        sql = """
        SELECT category, SUM(amount) as total_amount, COUNT(*) as transaction_count
        FROM expenses
        WHERE user_id = %s
        GROUP BY category
        ORDER BY total_amount DESC
        """
        return execute_query(sql, (user_id,), fetch_all=True)

    @staticmethod
    def get_monthly_summary(user_id):
        """Fetches total expenditure per month."""
        sql = """
        SELECT 
            DATE_FORMAT(expense_date, '%%Y-%%m') as month_label,
            SUM(amount) as total_amount
        FROM expenses
        WHERE user_id = %s
        GROUP BY month_label
        ORDER BY month_label DESC
        LIMIT 12
        """
        return execute_query(sql, (user_id,), fetch_all=True)
