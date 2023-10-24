import time
import logging

def log_execution_time(method):
    # on recupere la methode, on l'execute, on calcule le temps d'execution, on log le temps d'execution
    def wrapper(*args, **kwargs):
        start_time = time.time()
        output = method(*args, **kwargs)
        end_time = time.time()
        exec_time = end_time - start_time
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        log_message = f"{method.__name__} executed in {exec_time:.2f} seconds at {timestamp}"
        logging.info(log_message)

        return output

    return wrapper

# Configure logging to save to a file
logging.basicConfig(filename='methods_exec_logs.log', level=logging.INFO, format='%(message)s')