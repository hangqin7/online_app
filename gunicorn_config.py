# gunicorn_config.py

def post_fork(server, worker):
    """
    This hook is called in each worker process after it is forked.
    It starts the background thread that reads data from the database.
    """
    try:
        from application import start_reading  # adjust the module name if needed
        start_reading()
    except Exception as e:
        # You can log the error appropriately; for now we just print it.
        print("Error starting background thread:", e)
