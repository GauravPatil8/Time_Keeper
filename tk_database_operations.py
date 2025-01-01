import sqlite3
import os

class DatabaseOperations:
    def __init__(self):
        script_path = os.path.abspath(__file__)
        package_path = os.path.dirname(script_path)
        self.db_name = os.path.join(package_path, 'time_keeper.db')
        self.__setup()

    def __setup(self):
        """Setup the database and create the table if it doesn't exist."""
        query = """
            CREATE TABLE IF NOT EXISTS projects(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT,
                time_spent INTEGER,
                is_deleted INTEGER 
            )
        """
        self.__execute_query(query)

    def __execute_query(self, query, params=None):
        """
        Executes a query with optional parameters.
        
        Args:
            query (str): SQL query string.
            params (tuple): Tuple of values to substitute into the query.
        
        Returns:
            result (list or None): List of results for SELECT queries, None for others.
        """
        try:
                db_connection = sqlite3.connect(self.db_name)
                db_cursor = db_connection.cursor()

                if params:
                    result = db_cursor.execute(query, params)
                else:
                    result = db_cursor.execute(query)

                db_connection.commit()
                toReturn = result.fetchall() if query.strip().upper().startswith("SELECT") else None
                db_cursor.close()
                db_connection.close()
                return toReturn
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return None

    def create_project_entry(self, project_name):
        """Create a new project entry in the database."""
        query = """
            INSERT INTO projects (project_name, time_spent, is_deleted)
            VALUES (?, ?, ?)
        """
        self.__execute_query(query, (project_name, 0, 0))

    def update_project_time(self, project_name, seconds):
        """Update the time spent on a project."""
        query = """
            UPDATE projects SET time_spent = ?
            WHERE project_name = ?
        """
        self.__execute_query(query, (seconds, project_name))
    
    def delete_project_entry(self, project_name):
        """SOFT Delete a project from the database."""
        query = """
            UPDATE projects SET is_deleted = 1 WHERE project_name = ?
        """
        self.__execute_query(query, (project_name,))

    def reset_project_time(self, project_name):
        """Reset the time spent on a project to 0."""
        query = """
            UPDATE projects SET time_spent = ?
            WHERE project_name = ?
        """
        self.__execute_query(query, (0, project_name))

    def get_project_list(self):
        """Fetch all project names from the database."""
        query = "SELECT project_name FROM projects WHERE is_deleted == 0"
        return self.__execute_query(query)
    
    
    def get_project_time(self, project_name):
        """
        Fetch project time from the data base
        Args:
            project_name: name selected in the enum list
        
        Returns:
            time in seconds
        """

        query = """
            SELECT time_spent FROM projects
            WHERE
            project_name = ? 
        """
        return self.__execute_query(query,(project_name,))[0][0]
    
    def  get_total_time(self):
        """
        Fetch total time from the data base
        Args:
            None
        Returns:
            Time in Seconds
        """

        query = """
                SELECT SUM(time_spent) FROM projects
                """
        
        return self.__execute_query(query)[0][0]
    
    def check_project_name_availability(self,project_name):
        query = """
                SELECT COUNT(*)
                FROM projects
                WHERE project_name = ?;
                """
        return self.__execute_query(query, (project_name,))[0][0] == 0