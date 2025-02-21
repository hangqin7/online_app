import websocket
import json

# WebSocket API Gateway Endpoint
WS_ENDPOINT = "wss://s204arctwj.execute-api.eu-north-1.amazonaws.com/production/?type=online"

def on_message(ws, message):
    print("[Online App] Received from server:", message)

def on_open(ws):
    print("[Online App] Connected to WebSocket API Gateway")

    # Send a command to be forwarded to the local app
    command_message = {
        "command": "start_process",
        "params": {
            "speed": 50,
            "duration": 10
        }
    }

    ws.send(json.dumps(command_message))
    print(f"[Online App] Sent command: {command_message}")

def on_close(ws, close_status_code, close_msg):
    print(f"[Online App] Disconnected (code={close_status_code}, msg={close_msg})")

def on_error(ws, error):
    print(f"[Online App] WebSocket error: {error}")

# Start the WebSocket client
def start_online_ws():
    ws = websocket.WebSocketApp(
        WS_ENDPOINT,
        on_open=on_open,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error
    )
    ws.run_forever()

# Run the online WebSocket client
if __name__ == "__main__":
    start_online_ws()
