import random
import mysql.connector
import pandas as pd
from mysql.connector import Error, pooling
from config import *
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import configparser
import logging


class DataReader:
    def __init__(self, config_file=os.path.join(PROJECT_ROOT, "utils/db_config.ini"), buffer_length=BUFFER_length):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.host = self.config["mysql"]["host"]
        self.user = self.config["mysql"]["user"]
        self.password = self.config["mysql"]["password"]
        self.database = self.config["mysql"]["database"]
        self.table = self.config["mysql"]["table"]
        self.buffer_length = 30

        db_config = {
            "host": self.config["mysql"]["host"],
            "user": self.config["mysql"]["user"],
            "password": self.config["mysql"]["password"],
            "database": self.config["mysql"]["database"],
        }
        self.connection_pool = pooling.MySQLConnectionPool(
            pool_name="datalogger_pool",
            pool_size=5,
            pool_reset_session=True,
            **db_config
        )
        connection_url = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}/{self.database}"
        self.sql_engine = create_engine(connection_url, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=30,
                               pool_pre_ping=True)

        self.data_buffer = []

    def _connect(self):
        """Create a MySQL connection."""
        return self.connection_pool.get_connection()


    def read_data_to_buffer(self):
        """
        Read the last N rows (most recent based on 'timestamp') from the database table,
        convert each row to a dictionary (with column names as keys), and store them in self.data_buffer.
        """
        try:
            # Establish a connection using SQLAlchemy engine
            # engine = self._connect_alchemy()

            # Build a query to fetch the last N rows based on the timestamp.
            # We order by timestamp descending to get the most recent rows and then reverse them.
            query = f"""
                SELECT * FROM {self.table}
                ORDER BY timestamp DESC
                LIMIT {self.buffer_length}
            """
            # Read the query results into a DataFrame
            df = pd.read_sql(query, self.sql_engine)

            # Reverse the DataFrame so that the rows are in chronological order (oldest first)
            df = df.iloc[::-1]

            # Convert each row into a dictionary and store in self.data_buffer
            self.data_buffer = df.to_dict(orient="records")

        except Exception as e:
            logging.error(f"Error reading data to buffer: {e}")

    def fetch_data(self):
        """Fetch all data from the database."""
        try:
            # engine = self._connect_alchemy()  # Use SQLAlchemy engine
            query = "SELECT * FROM datalog"
            data = pd.read_sql(query, self.sql_engine)
            return data
        except Exception as e:
            print(f"Error querying data: {e}")
            return None

    def query_data(self, start_time, end_time):
        """Query historical data from the database for a specific time range."""
        try:
            # engine = self._connect_alchemy()  # Use SQLAlchemy engine
            query = f"""
                SELECT * FROM {self.table}
                WHERE timestamp BETWEEN %s AND %s
            """
            # Use pandas to execute the query using the SQLAlchemy engine
            data = pd.read_sql(query, self.sql_engine, params=(start_time, end_time))
            return data
        except Exception as e:
            print(f"Error querying data: {e}")

    def clear_old_logs(self, days):
        """
        Delete logs older than the specified number of days.
        :param days: Number of days to retain logs (e.g., 30 days).
        """
        try:
            # Calculate the cutoff timestamp
            cutoff_time = datetime.now() - timedelta(days=days)
            cutoff_time_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')

            # Use the SQLAlchemy engine to get a connection and execute the DELETE query
            with self.sql_engine.begin() as connection:
                query = text("DELETE FROM datalog WHERE timestamp < :cutoff_time")
                result = connection.execute(query, {"cutoff_time": cutoff_time_str})
                rows_deleted = result.rowcount
                logging.info(f"Deleted {rows_deleted} rows older than {days} days.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    data_reader = DataReader()
    data_reader.read_data_to_buffer()
    data_reader.clear_old_logs(4)
    print(data_reader.data_buffer)
