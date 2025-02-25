import time
from datetime import datetime, timedelta
import queue
import dash_bootstrap_components as dbc
import dash
import threading
import websocket
import json
from dash import no_update
from dash import dcc, no_update, callback_context
from dash.dependencies import Input, Output, State
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
app = dash.Dash(__name__, suppress_callback_exceptions=True, server=application, url_base_pathname='/dashboard/', external_stylesheets=[dbc.themes.BOOTSTRAP])
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
        # print(data_dict[-1])
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

# WebSocket API Gateway Endpoint
WS_ENDPOINT = "wss://s204arctwj.execute-api.eu-north-1.amazonaws.com/production/?type=online"

# Global variable to store the websocket connection
ws_client = None
message_from_server = None
ws_thread = None
ws_running = False

def on_message(ws, message):
    global message_from_server
    print("[Online App] Received from server:", message)
    try:
        data = json.loads(message)
        if data.get("status") == "ERROR":
            message_from_server = {'msg': data.get("message"), 'status': 'ERROR'}
        elif data.get("status") == "OK":
            message_from_server = {'msg': data.get("message"), 'status': 'SUCCESS'}
        elif data.get("message") == "Internal server error":
            message_from_server = {'msg': "API server error, cannot connect to local app", 'status': 'SERVER ERROR'}
    except Exception as e:
        print("Error parsing message:", e)

def on_open(ws):
    print("[Online App] Connected to WebSocket API Gateway")
    # Optionally, you can send an initial command here if needed
    # command_message = {"clientType": "online", "data": {"command": "lf"}}
    # ws.send(json.dumps(command_message))
    # print(f"[Online App] Sent command: {command_message}")

def on_close(ws, close_status_code, close_msg):
    global ws_client
    print(f"[Online App] Disconnected (code={close_status_code}, msg={close_msg})")
    ws_client = None

def on_error(ws, error):
    print(f"[Online App] WebSocket error: {error}")

def run_ws_client():
    """
    This function continuously tries to establish a WebSocket connection.
    If the connection is lost, it waits for 5 seconds before attempting to reconnect.
    """
    global ws_client, ws_running
    while ws_running:
        try:
            ws = websocket.WebSocketApp(
                WS_ENDPOINT,
                on_open=on_open,
                on_message=on_message,
                on_close=on_close,
                on_error=on_error
            )
            ws_client = ws  # update the global connection
            ws.run_forever()  # blocks until the connection is closed or an error occurs
        except Exception as e:
            print("[Online App] Exception in WebSocket thread:", e)
        # Wait a few seconds before attempting to reconnect
        if ws_running:
            time.sleep(5)
    print("[Online App] Exiting WebSocket thread.")

def send_ws_command(command):
    """
    Sends a command (e.g. "lf") to the WebSocket.
    This function is safe to call from within a Dash callback.
    """
    global ws_client, message_from_server
    if ws_client and ws_client.sock and ws_client.sock.connected:
        command_message = {
            "clientType": "online",
            "data": {
                "command": command
            }
        }
        try:
            ws_client.send(json.dumps(command_message))
            print(f"[Online App] Sent command: {command_message}")
        except Exception as e:
            print("[Online App] Failed to send command:", e)
    else:
        print("[Online App] WebSocket not connected. Cannot send command.")
        message_from_server = {'msg': "WebSocket not connected. Cannot send command", 'status': 'ERROR'}


def start_ws():
    global ws_thread, ws_running
    if not ws_running:
        ws_running = True
        ws_thread = threading.Thread(target=run_ws_client, daemon=True)
        ws_thread.start()
        return "Websocket started."
    else:
        return "Websocket already running."

def stop_ws():
    global ws_thread, ws_running, ws_client
    if ws_running:
        ws_running = False  # Signal the thread to exit its loop
        if ws_client and ws_client.sock and ws_client.sock.connected:
            try:
                ws_client.close()  # Close the connection to break out of run_forever
            except Exception as e:
                print("[Online App] Exception while closing WebSocket:", e)
        if ws_thread is not None:
            ws_thread.join(timeout=10)  # Wait (with timeout) for the thread to finish
        ws_thread = None
        return "Websocket stopped."
    else:
        return "Websocket is not running."

@app.callback(
    Output("status-output", "children"),
    [Input("btn-start", "n_clicks"),
     Input("btn-stop", "n_clicks")]
)
def control_ws(n_start, n_stop):
    # Determine which button was pressed
    ctx = dash.callback_context
    if not ctx.triggered:
        return "Status: Websocket started." if ws_running else "Status: Websocket not started."

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == "btn-start":
        message = start_ws()
    elif button_id == "btn-stop":
        message = stop_ws()
    else:
        message = "No action"

    return f"Status: {message}"


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

    # elif tab == "stack2":
    #     return stack2_content()


@app.callback(
    Output("policy-modal", "is_open"),
    [
        Input("open-policy-modal", "n_clicks"),
        Input("cancel-policy", "n_clicks"),
        Input("confirm-policy", "n_clicks"),
    ],
    [State("policy-modal", "is_open")],
)
def toggle_modal(open_click, cancel_click, confirm_click, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return is_open
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id in ["open-policy-modal", "cancel-policy", "confirm-policy"]:
        return not is_open
    return is_open

# Callback to update the energy policy based on user confirmation
@app.callback(
    [Output("policy-store", "data"),
        # Output("energy-policy-display", "value"),
     Output("policy-toast", "children"),
     Output("policy-toast", "is_open")],
    [Input("confirm-policy", "n_clicks")],
    [State("energy-policy-selection", "value"),
     # State("energy-policy-display", "value"),
     State("policy-store", "data"),]
)
def update_policy(n_clicks, selected_policy, current_policy):
    # global running_policy
    if not n_clicks:
        # raise dash.exceptions.PreventUpdate
        return data_dict[-1]['running_policy'], no_update, no_update

    if selected_policy == data_dict[-1]['running_policy']:
        message = "No changes applied. Energy policy remains unchanged."
        return data_dict[-1]['running_policy'], message, True
        # return message, True
    else:
        # running_policy = selected_policy
        send_ws_command(selected_policy)
        # time.sleep(5)
        message = (f"Try to change the energy policy updated to: {energy_dict.get(selected_policy)},"
                   f" Please wait a few seconds")
        return selected_policy, message, True
        # return message, True


@app.callback(
    [Output("energy-policy-display", "value"),
     Output("energy-policy-selection", "value")],
    [Input("interval-main", "n_intervals"),
     Input("policy-store", "data")]
)
def sync_policy_display(n_policy, store_data):
    # print("finding energy policy")
    return data_dict[-1]['running_policy'], data_dict[-1]['running_policy']


@app.callback(
    [Output("error-modal", "is_open"),
     Output("error-modal-content", "children")],
    [Input("interval-error-check", "n_intervals"),
     Input("close-error-modal", "n_clicks")],
    [State("error-modal", "is_open")]
)
def check_error(n_intervals, close_clicks, is_open):
    global message_from_server
    ctx = dash.callback_context
    # Check if the Close button was clicked
    if ctx.triggered and ctx.triggered[0]["prop_id"].split('.')[0] == "close-error-modal" and is_open:
        return False, no_update
    # If the error_message variable is set, open the modal
    if message_from_server:
        msg = message_from_server['status']+'! '+message_from_server['msg']+'.'
        message_from_server = None  # Reset the error after showing it
        return True, msg
    # Otherwise, do not change the modal state
    return is_open, no_update


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
def update_main_page(n_main):
    soc_unit1 = data_dict[-1]['soc_percent']
    return float(soc_unit1)


# Callback to update the real-time curves
@app.callback(
    [Output("voltage-curve", "figure"),
     Output("current-curve", "figure"),
     Output("power-curve", "figure"),
     Output("soc-curve", "figure"),
     Output("temp-curve", "figure"),
     Output("energy-curve", "figure"),

     Output("dynamic-indicators-table1", "data"),
     Output("dynamic-indicators-table2", "data")],

     # Output("dynamic-indicators-table-body", "children")],

     Output("connection-status", "children"),
     Output("connection-status", "style"),

     Input("interval-component", "n_intervals")
)
def update_real_time_data(n):  # the data will update according to the updated_frequency set in the stack1.py
    # if connection_state:
    latest_data_point = data_dict[-1]

    # Create the data for the voltage curve
    voltage_trace = get_trace_obj('voltage_v', data_dict)
    current_trace = get_trace_obj('current_a', data_dict)
    power_trace = get_trace_obj('pack_power_kw', data_dict)
    soc_trace = get_trace_obj('soc_percent', data_dict)
    temp_trace = get_trace_obj('stack_temp_max', data_dict)
    available_energy_trace = get_trace_obj('available_energy_kwh', data_dict)

    last_update_time = datetime.fromisoformat(str(latest_data_point['timestamp']))
    time_bound = datetime.now() - timedelta(minutes=10)
    # print(last_update_time)
    # print(time_bound)
    time_color = "red" if last_update_time < time_bound else "green"

    # Update the table data with new values
    table_data1 = [
        {"indicator": "pack SOC (%)", "value": f"{latest_data_point['soc_percent']}%"},
        {"indicator": "pack voltage (V)", "value": f"{latest_data_point['voltage_v']}"},
        {"indicator": "pack current (A)", "value": f"{latest_data_point['current_a']}"},
        {"indicator": "pack power (kw)", "value": f"{latest_data_point['pack_power_kw']}"},
        {"indicator": "max stack temperature (°C)", "value": f"{latest_data_point['stack_temp_max']}"},
        {"indicator": "measured energy (kwh)", "value": f"{latest_data_point['measured_energy_kwh']}"},
    ]
    table_data2 = [
        {"indicator": "AC power (kw)", "value": f"{latest_data_point['ac_power_kw']}"},
        {"indicator": "DC power (kw)", "value": f"{latest_data_point['dc_power_kw']}"},
        {"indicator": "storage power (kw)", "value": f"{latest_data_point['storage_power_kw']}"},
        {"indicator": "pack SOH (%)", "value": f"{latest_data_point['soh_percent']}%"},
        {"indicator": "available energy (kwh)", "value": f"{latest_data_point['available_energy_kwh']}"},
        {"indicator": "available charge (Ah)", "value": f"{latest_data_point['available_charge_ah']}"},
    ]
    return (
        {"data": [voltage_trace], "layout": get_figure_layout('pack voltage (V)')},
        {"data": [current_trace], "layout": get_figure_layout('pack current (A)')},
        {"data": [power_trace], "layout": get_figure_layout('pack power (kW)')},
        {"data": [soc_trace], "layout": get_figure_layout('pack SOC (%)')},
        {"data": [temp_trace], "layout": get_figure_layout('max stack temperature (°C)')},
        {"data": [available_energy_trace], "layout": get_figure_layout('available energy (kWh)')},
        table_data1, table_data2,
        str(last_update_time).replace('T', '\t'),
        {"color": time_color, "fontWeight": "bold"}
    )


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
    # start_ws()
    application.run(host="0.0.0.0", port=5000)

