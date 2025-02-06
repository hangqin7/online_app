import random
import mysql.connector
from mysql.connector import Error, pooling
import pandas as pd
from collections import deque
from utils.config import *
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import configparser
import logging


class DataLogger:
    """
    DataLogger using MySQL for data streaming and data pipeline.
    Data input: {'indicator': values, ...}
    """

    def __init__(self, config_file=os.path.join(PROJECT_ROOT, "utils/db_config.ini"), indicators=INDICATORS, buffer_duration=BUFFER_duration):
        # self.host = host
        # self.user = user
        # self.password = password
        # self.database = database
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.host = self.config["mysql"]["host"]
        self.user = self.config["mysql"]["user"]
        self.password = self.config["mysql"]["password"]
        self.database = self.config["mysql"]["database"]

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
        self.indicators = indicators  # Default indicators
        self.real_time_buffer = deque(maxlen=buffer_duration * 60 // streaming_interval)  # Buffer for the last N minutes of data
        self._initialize_database()

    def _connect(self):
        """Create a MySQL connection."""
        return self.connection_pool.get_connection()
        # return mysql.connector.connect(
        #     host=self.host,
        #     user=self.user,
        #     password=self.password,
        #     database=self.database
        # )

    def _connect_alchemy(self):
        """Create a SQLAlchemy connection."""
        # Creating a connection URL for SQLAlchemy
        connection_url = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}/{self.database}"
        engine = create_engine(connection_url)
        return engine

    def _initialize_database(self):
        """Create the database and table if they don't exist."""
        try:
            # Step 1: Connect to MySQL server without specifying a database
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password)  # Connect to the server, but not a specific database yet
            cursor = conn.cursor()

            # Step 2: Create the database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            conn.commit()  # Commit the changes (create the database)
            conn.close()  # Close the initial connection

            # Step 3: Reconnect to the server, now specifying the database
            conn = self._connect()  # Connect to the newly created database
            cursor = conn.cursor()

            # Step 4: Dynamically create the table based on the indicators list
            columns = ", ".join([f"{indicator} FLOAT" for indicator in self.indicators[1:]])  # Exclude timestamp
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS datalog (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME,
                    {columns}
                )
            """)

            # Step 5: Commit the changes and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            print("Initialized the database.")
        except Error as e:
            print(f"Error initializing database: {e}")

    def log_data_to_db(self, data):
        """
        Insert data dynamically into the database.
        Args:
            data (dict): A dictionary containing key-value pairs for indicators.
        """
        timestamp = datetime.now().isoformat()
        data['timestamp'] = timestamp

        # Ensure all indicators exist in the provided data
        assert all(indicator in data for indicator in self.indicators), "Missing data for some indicators"

        # Dynamically create the column names and placeholders
        columns = ", ".join(self.indicators)  # Example: "timestamp, voltage, current, power"
        placeholders = ", ".join(["%s"] * len(self.indicators))  # Example: "%s, %s, %s, %s"

        # Extract the corresponding values from the data dictionary
        values = tuple(data[indicator] for indicator in self.indicators)

        # Construct the SQL query
        query = f"INSERT INTO datalog ({columns}) VALUES ({placeholders})"

        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error logging data: {e}")

    def log_data_to_buffer(self, data):
        timestamp = datetime.now().isoformat()
        data['timestamp'] = timestamp
        assert all(indicator in data for indicator in self.indicators), "Missing data for some indicators"
        self.real_time_buffer.append([data[indicator] for indicator in self.indicators])

    def fetch_data(self):
        """Fetch all data from the database."""
        try:
            engine = self._connect_alchemy()  # Use SQLAlchemy engine
            query = "SELECT * FROM datalog"
            data = pd.read_sql(query, engine)
            return data
        except Exception as e:
            print(f"Error querying data: {e}")
            return None

    def query_data(self, start_time, end_time):
        """Query historical data from the database for a specific time range."""
        try:
            engine = self._connect_alchemy()  # Use SQLAlchemy engine
            query = f"""
                SELECT * FROM datalog
                WHERE timestamp BETWEEN %s AND %s
            """
            # Use pandas to execute the query using the SQLAlchemy engine
            data = pd.read_sql(query, engine, params=(start_time, end_time))
            return data
        except Exception as e:
            print(f"Error querying data: {e}")

    # def export_data(self, start_time, end_time, file_path=LOG_PATH):
    #     """Export data within a time range to a CSV file."""
    #     data = self.query_data(start_time, end_time)
    #     file_path = os.path.join(file_path, "export.csv")
    #     if data is not None:
    #         data.to_csv(file_path, index=False)
    #         print(f"Data exported to {file_path}")

    def get_realtime_data(self):
        """Retrieve the last `buffer_duration` minutes of real-time data."""
        return pd.DataFrame(self.real_time_buffer, columns=self.indicators)

    def add_indicator(self, new_indicator):
        """Add a new indicator to the database schema if it does not exist."""
        try:
            conn = self._connect()
            cursor = conn.cursor()

            # Check if the indicator column already exists in the database schema
            query = f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'datalog' AND TABLE_SCHEMA = '{self.database}'
            """
            cursor.execute(query)
            columns = [column[0] for column in cursor.fetchall()]

            if new_indicator in columns:
                print(f"Indicator '{new_indicator}' already exists in the database.")
                cursor.close()
                conn.close()
                return

            # Add the new column (indicator) to the database
            cursor.execute(f"ALTER TABLE datalog ADD COLUMN {new_indicator} FLOAT")
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Indicator '{new_indicator}' added successfully.")
        except Error as e:
            print(f"Error adding indicator: {e}")

    def clear_old_logs(self, days):
        """
        Delete logs older than the specified number of days.
        :param days: Number of days to retain logs (e.g., 30 days).
        """
        try:
            # Calculate the cutoff timestamp
            cutoff_time = datetime.now() - timedelta(days=days)
            cutoff_time_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')

            # Acquire a connection from the pool
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()

            # Prepare and execute the DELETE query
            query = f"DELETE FROM datalog WHERE timestamp < %s"
            cursor.execute(query, (cutoff_time_str,))

            # Commit the changes
            connection.commit()
            rows_deleted = cursor.rowcount
            logging.info(f"Deleted {rows_deleted} rows older than {days} days.")
        except Error as e:
            logging.error(f"MySQL error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        finally:
            # Ensure resources are released
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def close(self):
        if self.connection_pool:
            self.connection_pool._remove_connections()
            logging.info("Connection pool closed.")


def synthetic_data_poll():
    voltage = random.uniform(45, 55)  # Simulating voltage between 45V and 55V
    current = random.uniform(5, 15)  # Simulating current between 5A and 15A
    power = voltage * current  # Power = Voltage * Current (P = V * I)
    soc = random.uniform(70, 100)  # Simulating SOC between 70% and 100%
    temperature = random.uniform(20, 30)
    return {'voltage': voltage, 'current': current, 'power': power, 'soc': soc, 'temperature': temperature}



if __name__ == "__main__":
    logger = DataLogger()
    # for key in key_list:
    #     logger.add_indicator(key)
    # for _ in range(100):  # Stream 10 entries
    #     voltage = round(random.uniform(220, 240), 2)
    #     current = round(random.uniform(5, 15), 2)
    #     power = round(voltage * current / 1000, 2)  # Calculate power in kW
    #     soc = round(random.uniform(80, 90), 2)
    #     # logger.add_data(voltage, current, power)
    #     # time.sleep(1)  # Simulate 1-second intervals
    #     logger.log_data_to_db({'voltage': voltage, 'current': current, 'power': power, 'soc': soc})
    #     logger.log_data_to_buffer({'voltage': voltage, 'current': current, 'power': power, 'soc': soc})
    #
    #     real_time_data = logger.get_realtime_data()
    #     # print(real_time_data.tail(1)['voltage'].values[-1])
    #     print(real_time_data)
    #
    # # print(logger.fetch_data())
    # #
    # # print(datetime(2025, 1, 14, 16, 11, 00))
    # logger.export_data(datetime(2025, 1, 15, 11, 18, 00).isoformat(),
    #                    datetime(2025, 1, 15, 11, 20, 00).isoformat())

