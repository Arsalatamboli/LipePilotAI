from app.db import execute_query

class TaskModel:
    @staticmethod
    def create_task(user_id, title, description='', priority='Medium', estimated_hours=1.0, due_date=None):
        """Creates a new task for a user."""
        sql = """
        INSERT INTO tasks (user_id, title, description, priority, status, estimated_hours, due_date)
        VALUES (%s, %s, %s, %s, 'Pending', %s, %s)
        """
        return execute_query(sql, (user_id, title, description, priority, estimated_hours, due_date), commit=True)

    @staticmethod
    def get_by_user(user_id, status=None):
        """Fetches tasks for a user, optionally filtered by status."""
        if status:
            sql = "SELECT * FROM tasks WHERE user_id = %s AND status = %s ORDER BY due_date ASC, priority DESC"
            return execute_query(sql, (user_id, status), fetch_all=True)
        else:
            sql = "SELECT * FROM tasks WHERE user_id = %s ORDER BY status ASC, due_date ASC"
            return execute_query(sql, (user_id,), fetch_all=True)

    @staticmethod
    def update_status(task_id, user_id, status):
        """Updates status of a task ('Pending', 'In Progress', 'Completed')."""
        sql = "UPDATE tasks SET status = %s WHERE id = %s AND user_id = %s"
        execute_query(sql, (status, task_id, user_id), commit=True)

    @staticmethod
    def delete_task(task_id, user_id):
        """Deletes a task."""
        sql = "DELETE FROM tasks WHERE id = %s AND user_id = %s"
        execute_query(sql, (task_id, user_id), commit=True)

    @staticmethod
    def get_task_summary(user_id):
        """Returns task counts by status and priority."""
        sql = """
        SELECT 
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending_count,
            SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_count,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_count,
            SUM(CASE WHEN priority = 'High' AND status != 'Completed' THEN 1 ELSE 0 END) as high_priority_pending
        FROM tasks
        WHERE user_id = %s
        """
        return execute_query(sql, (user_id,), fetch_one=True)
