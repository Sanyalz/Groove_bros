# -*- coding: utf-8 -*-from pydub import AudioSegment
import logging
import socket

# Logging file
logging.basicConfig(filename='Alex_Luzhnov_client_server.log', level=logging.INFO,
                    format='\n%(asctime)s - %(levelname)s - %(message)s')

FORMAT = 'utf-8'
DISCONNECT_MSG = "EXIT"
COMMANDS = ['MES', 'LOG', 'REG', 'VOTE']

def write_to_log(data):
    logging.info(data)
    try:
        print(data + ' - added to log file')
    except:
        pass