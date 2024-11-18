import logging
from abc import ABC, abstractmethod
# Logging file
logging.basicConfig(filename='Alex_Luzhnov_client_server.log', level=logging.INFO,
                    format='\n%(asctime)s - %(levelname)s - %(message)s')

FORMAT = 'utf-8'
DISCONNECT_MSG = "EXIT"
COMMANDS_26 = ["TIME", "RAND", "NAME"]
COMMANDS_27 = ["DIR", "DELETE", "COPY", "EXECUTE", "TAKE_SCREENSHOT", "SEND_PHOTO"]

def write_to_log(data):
    logging.info(data)
    print(data + ' - added to log file')