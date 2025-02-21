import time
from datetime import datetime, timedelta
import dash
import threading
from dash import no_update
from dash.dependencies import Input, Output
from tabs.main_content import main_content, dash_layout
from tabs.stack1 import stack1_content, stack1_statics, stack1_dynamics
from tabs.stack2 import stack2_content
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from utils.utils_data import DataReader
from utils.utils_visualization import get_trace_obj, get_figure_layout
# import pymysql
from mysql.connector import pooling
import configparser
from config import *

header_width = 120
theme_color = "#000000"  # #2d4425
theme_bgcolor = "#1c1c1c"  #1c1c1c

#######################################################################################################
# Flask Setup
application = Flask(__name__)
application.secret_key = 'my_secret_key'

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'

def get_db_connection():
    config_file = os.path.join(PROJECT_ROOT, "utils/user_config.ini")
    config = configparser.ConfigParser()
    config.read(config_file)
    db_config = {
        "host": config["mysql"]["host"],
        "user": config["mysql"]["user"],
        "password": config["mysql"]["password"],
        "database": config["mysql"]["database"],
    }
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="datalogger_pool",
        pool_size=5,
        pool_reset_session=True,
        **db_config
    )
    return connection_pool.get_connection()


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id
##########################################################################################################


# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, server=application, url_base_pathname='/dashboard/')
# data_dict and logger
data_reader = DataReader()
data_reader.read_data_to_buffer()
data_dict = data_reader.data_buffer
data_reader.clear_old_logs(days=3)
connection_state = False


def read_from_db():
    global data_dict
    while True:
        data_reader.read_data_to_buffer()
        data_dict = data_reader.data_buffer
        time.sleep(streaming_interval)


def start_reading():
    read_thread = threading.Thread(target=read_from_db, daemon=True)
    read_thread.start()


# Protect the dashboard route with login_required decorator
@app.server.before_request
def before_request():
    """Redirect to login page if not authenticated"""
    if not current_user.is_authenticated and request.endpoint != 'login' and request.endpoint != 'register':
        return redirect(url_for('login'))

# App layout
app.layout = dash_layout()

######################################################################
# Route
@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    connection.close()
    if user:
        return User(user[0])
    return None

@application.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            connection.close()
            return "User already exists. Please login.", 400

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()
        connection.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login Route
@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            user_obj = User(user[0])  # Assuming the 'id' is the first column
            login_user(user_obj)
            return redirect('/dashboard/')
        else:
            return "Invalid credentials", 401

    return render_template('login.html')


# Home Route (Redirect to login if not logged in)
@application.route('/')
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
@app.callback(
    [Output("voltage-curve", "figure"),
     Output("current-curve", "figure"),
     Output("power-curve", "figure"),
     Output("soc-curve", "figure"),
     Output("temp-curve", "figure"),

     Output("dynamic-indicators-table", "data")],
     # Output("dynamic-indicators-table-body", "children")],

     Output("connection-status", "children"),
     Output("connection-status", "style"),

     Input("interval-component", "n_intervals")
)
def update_real_time_data(n):  # the data will update according to the updated_frequency set in the stack1.py
    # if connection_state:
    latest_data_point = data_dict[-1]
    # voltage, current, power, soc = real_time_data_point['voltage'].values(), real_time_data_point['current'].values(), real_time_data_point['power'].values(), real_time_data_point['soc'].values()
    # print(voltage, current, power, soc)

    # Create the data for the voltage curve
    voltage_trace = get_trace_obj('voltage_v', data_dict)
    current_trace = get_trace_obj('current_a', data_dict)
    power_trace = get_trace_obj('pack_power_kw', data_dict)
    soc_trace = get_trace_obj('soc_percent', data_dict)
    temp_trace = get_trace_obj('stack_temp_max', data_dict)


    last_update_time = datetime.fromisoformat(str(latest_data_point['timestamp']))
    time_bound = datetime.now() - timedelta(minutes=10)
    print(last_update_time)
    print(time_bound)
    time_color = "red" if last_update_time < time_bound else "green"

    # Update the table data with new values
    table_data = [
        {"indicator": "pack SOC", "value": f"{latest_data_point['soc_percent']}%"},
        {"indicator": "pack voltage (V)", "value": f"{latest_data_point['voltage_v']}"},
        {"indicator": "pack current (A)", "value": f"{latest_data_point['current_a']}"},
        {"indicator": "pack power (kw)", "value": f"{latest_data_point['pack_power_kw']}"},
        {"indicator": "max stack temperature (°C)", "value": f"{latest_data_point['stack_temp_max']}"},
        {"indicator": "State of the Battery Bank", "value": "Healthy"},
    ]
    return (
        {"data": [voltage_trace], "layout": get_figure_layout('pack voltage')},
        {"data": [current_trace], "layout": get_figure_layout('pack current')},
        {"data": [power_trace], "layout": get_figure_layout('pack power')},
        {"data": [soc_trace], "layout": get_figure_layout('pack SOC')},
        {"data": [temp_trace], "layout": get_figure_layout('Max stack temperature')},
        table_data,
        str(last_update_time).replace('T', '\t'),
        {"color": time_color, "fontWeight": "bold"}
    )

    # else:
    #     return (
    #         no_update,
    #         no_update,
    #         no_update,
    #         no_update,
    #         no_update,
    #         no_update,
    #         "No",
    #         {"color": "red", "fontWeight": "bold"}
    #     )



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
    start_reading()
    application.run(debug=True, port=5000)

