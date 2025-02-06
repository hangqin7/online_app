import dash
import threading
from dash import dcc, html, no_update
from dash.dependencies import Input, Output, State
from tabs.main_content import main_content, dash_layout
from tabs.stack1 import stack1_content, stack1_statics, stack1_dynamics
from tabs.stack2 import stack2_content
from utils.utils_data import DataLogger, synthetic_data_poll
from utils.utils_api import build_datapack
from utils.utils_visualization import get_trace_obj, get_figure_layout
from datetime import datetime
from dash.exceptions import PreventUpdate
from flask import Flask, render_template, redirect, url_for, request, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# import pymysql
from mysql.connector import Error, pooling
from pymodbus.client import ModbusTcpClient
import time
import configparser
# from config import *

import pandas as pd
import random
import plotly.graph_objs as go



header_width = 120
theme_color = "#000000"  # #2d4425
theme_bgcolor = "#1c1c1c"  #1c1c1c

#######################################################################################################
# Flask Setup
server = Flask(__name__)
server.secret_key = 'my_secret_key'

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = 'login'

# MySQL Database Connection Setup
# def get_db_connection():
#     return pymysql.connect(
#         host='localhost',
#         user='ems_user',
#         password='e_tothe_m_tothe_s_is_ems2025!',
#         database='user_manager'
#     )
# def get_db_connection():
#     config_file = os.path.join(PROJECT_ROOT, "utils/user_config.ini")
#     config = configparser.ConfigParser()
#     config.read(config_file)
#     db_config = {
#         "host": config["mysql"]["host"],
#         "user": config["mysql"]["user"],
#         "password": config["mysql"]["password"],
#         "database": config["mysql"]["database"],
#     }
#     connection_pool = pooling.MySQLConnectionPool(
#         pool_name="datalogger_pool",
#         pool_size=5,
#         pool_reset_session=True,
#         **db_config
#     )
#     return connection_pool.get_connection()




# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id
##########################################################################################################


# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, server=server, url_base_pathname='/dashboard/')
# data_dict and logger
# data_logger = DataLogger()
# data_logger.clear_old_logs(days=3)
data_lock = threading.Lock()
connection_state = False


# Protect the dashboard route with login_required decorator
# @app.server.before_request
# def before_request():
#     """Redirect to login page if not authenticated"""
#     if not current_user.is_authenticated and request.endpoint != 'login' and request.endpoint != 'register':
#         return redirect(url_for('login'))

# App layout
app.layout = dash_layout()

######################################################################
# Route
# @login_manager.user_loader
# def load_user(user_id):
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
#     user = cursor.fetchone()
#     connection.close()
#     if user:
#         return User(user[0])
#     return None
#
# @server.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         connection = get_db_connection()
#         cursor = connection.cursor()
#         cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#         existing_user = cursor.fetchone()
#
#         if existing_user:
#             connection.close()
#             return "User already exists. Please login.", 400
#
#         cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
#         connection.commit()
#         connection.close()
#
#         return redirect(url_for('login'))
#
#     return render_template('register.html')
#
# # Login Route
# @server.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         connection = get_db_connection()
#         cursor = connection.cursor()
#         cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
#         user = cursor.fetchone()
#         connection.close()
#
#         if user:
#             user_obj = User(user[0])  # Assuming the 'id' is the first column
#             login_user(user_obj)
#             return redirect('/dashboard/')
#         else:
#             return "Invalid credentials", 401
#
#     return render_template('login.html')


# Home Route (Redirect to login if not logged in)
@server.route('/')
def home():
    # if current_user.is_authenticated:
    return redirect('/dashboard/')
    # return redirect(url_for('login'))
#######################################################################

@app.callback(
    Output('url-redirect', 'href'),
    Input('logout-btn', 'n_clicks')
)
def logout(n_clicks):
    if n_clicks:
        logout_user()  # Log out the user
        return '/login'  # Redirect to login page
    return dash.no_update

# Update content based on selected tab: main, stack1, stack2
@app.callback(
    Output("content", "children"),
    Input("tabs", "value"),
)
def render_content(tab):
    if tab == "main":
        return main_content()

    elif tab == "stack1":
        return stack1_content()

    elif tab == "stack2":
        return stack2_content()


# Callback to update the content based on the dropdown selection
@app.callback(
    Output("stack1-indicator-content", "children"),
    Input("stack1-indicator-dropdown", "value")
)
def display_stack1_indicators(indicator_type):
    if indicator_type == "static":
        return stack1_statics()
    elif indicator_type == "dynamic":
        return stack1_dynamics()


@app.callback(
    Output("battery-level-1", "value"),
    Input("interval-main", "n_intervals"),
)
def update_main_page(n):
    if connection_state:
        pass
        # real_time_data_series = data_logger.get_realtime_data()
        # real_time_data_point = real_time_data_series.tail(1)
        # soc_unit1 = real_time_data_point['soc_percent'].values[-1]
        # return soc_unit1
    else:
        return no_update


# Callback to update the real-time curves
# @app.callback(
#     [Output("voltage-curve", "figure"),
#      Output("current-curve", "figure"),
#      Output("power-curve", "figure"),
#      Output("soc-curve", "figure"),
#      Output("temp-curve", "figure"),
#
#      Output("dynamic-indicators-table", "data")],
#      # Output("dynamic-indicators-table-body", "children")],
#
#      Output("connection-status", "children"),
#      Output("connection-status", "style"),
#
#      Input("interval-component", "n_intervals")
# )
# def update_real_time_data(n):  # the data will update according to the updated_frequency set in the stack1.py
#     # Generate new random data
#     # data_dict = synthetic_data_poll()
#     # data_dict = modbus_poll()
#     # Generate updated rows
#     # table_rows = [
#     #     html.Tr([html.Td(row["indicator"]), html.Td(row["value"])]) for row in table_data
#     # ]
#     # Return the updated figures and table data
#     if connection_state:
#         real_time_data_series = data_logger.get_realtime_data()
#         real_time_data_point = real_time_data_series.tail(1)
#
#         # voltage, current, power, soc = real_time_data_point['voltage'].values(), real_time_data_point['current'].values(), real_time_data_point['power'].values(), real_time_data_point['soc'].values()
#         # print(voltage, current, power, soc)
#
#         # Create the data for the voltage curve
#         voltage_trace = get_trace_obj('voltage_v', real_time_data_series)
#         current_trace = get_trace_obj('current_a', real_time_data_series)
#         power_trace = get_trace_obj('pack_power_kw', real_time_data_series)
#         soc_trace = get_trace_obj('soc_percent', real_time_data_series)
#         temp_trace = get_trace_obj('stack_temp_max', real_time_data_series)
#
#         # Update the table data with new values
#         table_data = [
#             {"indicator": "pack SOC", "value": f"{real_time_data_point['soc_percent'].values[-1]:.2f}%"},
#             {"indicator": "pack voltage (V)", "value": f"{real_time_data_point['voltage_v'].values[-1]:.2f}"},
#             {"indicator": "pack current (A)", "value": f"{real_time_data_point['current_a'].values[-1]:.2f}"},
#             {"indicator": "pack power (kw)", "value": f"{real_time_data_point['pack_power_kw'].values[-1]:.2f}"},
#             {"indicator": "max stack temperature (°C)", "value": f"{real_time_data_point['stack_temp_max'].values[-1]:.2f}"},
#             {"indicator": "State of the Battery Bank", "value": "Healthy"},
#         ]
#         return (
#             {"data": [voltage_trace], "layout": get_figure_layout('pack voltage')},
#             {"data": [current_trace], "layout": get_figure_layout('pack current')},
#             {"data": [power_trace], "layout": get_figure_layout('pack power')},
#             {"data": [soc_trace], "layout": get_figure_layout('pack SOC')},
#             {"data": [temp_trace], "layout": get_figure_layout('Max stack temperature')},
#             table_data,
#             "Yes",
#             {"color": "green", "fontWeight": "bold"}
#         )
#
#     else:
#         return (
#             no_update,
#             no_update,
#             no_update,
#             no_update,
#             no_update,
#             no_update,
#             "No",
#             {"color": "red", "fontWeight": "bold"}
#         )



# @app.callback(
#     Output("log-download", "data"),
#     [   Input("download-button", "n_clicks"),
#         State("start-time-year", "value"),
#         State("start-time-month", "value"),
#         State("start-time-day", "value"),
#         State("start-time-hour", "value"),
#         State("start-time-minute", "value"),
#         State("end-time-year", "value"),
#         State("end-time-month", "value"),
#         State("end-time-day", "value"),
#         State("end-time-hour", "value"),
#         State("end-time-minute", "value")
#     ],
# )
# def download_log_data(n_clicks, start_year, start_month, start_day, start_hour, start_minute, end_year, end_month, end_day, end_hour, end_minute):
#     if n_clicks == 0:
#         raise PreventUpdate
#     try:
#         # Validate inputs
#         if None in [start_year, start_month, start_day, start_hour, start_minute, end_year, end_month, end_day, end_hour, end_minute]:
#             raise ValueError("All fields must be filled.")
#
#         start_time = datetime(start_year, start_month, start_day, start_hour, start_minute, 00).isoformat()
#         end_time = datetime(end_year, end_month, end_day, end_hour, end_minute, 00).isoformat()
#
#         if start_time >= end_time:
#             raise ValueError("Start time must be before end time.")
#         df = data_logger.query_data(start_time, end_time)
#         return dcc.send_data_frame(df.to_csv, "log_data.csv")
#
#     except Exception as e:
#         print(f"Error: {e}")
#         return None


# Run the app
if __name__ == "__main__":
    # app.run_server(debug=True)
    server.run(debug=False)

