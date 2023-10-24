import time
import logging

def log_execution_time(method):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = method(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        log_message = f"{method.__name__} executed in {execution_time:.2f} seconds at {timestamp}"
        logging.info(log_message)

        return result

    return wrapper

# Configure logging to save to a file
logging.basicConfig(filename='execution_logs.log', level=logging.INFO, format='%(message)s')