import logging

def configure_logging():
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(message)s')

def log_message(message):
    logging.info(message)
