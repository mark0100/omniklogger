#!/usr/bin/python
import socket
import logging
import logging.handlers
from logging.config import fileConfig
import InverterMsg  # Import the Msg handler
import datetime
import time
import os
import sys
import configparser
from PluginLoader import PluginBase

def expandPath(path):
    """
    Expand relative path to absolute path.

    Args:
        path: file path

    Returns: absolute path to file

    """
    if os.path.isabs(path):
        return path
    else:
        return os.path.dirname(os.path.abspath(__file__)) + "/" + path

maxConnRetries = 10
connected = False
retries = 1

config = None
logger = None
msgCount = 0
msgErrorCount = 0
msgAknowledgeCount = 0
pluginRuns = 0

# Load the config settings
configFile = expandPath('config.ini')

config = configparser.RawConfigParser()
config.read(configFile)

# Load the logging settings
fileConfig(expandPath('logging.ini'))
logger = logging.getLogger()

logger.info("Starting omniklogger") 

#TODO: Change "Aknowledge" to "Confirmation" as the second message after a data message
# really is a confirmation message. 

# TODO: Howto pass the config and logger vars to the plugins on creation
# instead of passing them in the process_message function?
#PluginBase.config = config
#PluginBase.logger = logger

# Load output plugins
# Prepare path for plugin loading
sys.path.append(expandPath('outputs'))

enabled_plugins = config.get('general', 'enabled_plugins').split(',')
for plugin_name in enabled_plugins:
    plugin_name = plugin_name.strip()
    logger.info('Importing output plugin: ' + plugin_name)
    __import__(plugin_name)

serial = str.encode(config.get('inverter', 'serial'))

localIP = config.get('UDPListener', 'localIP')
localPort = int(config.get('UDPListener', 'localPort'))

# Try several times to bind to the socket because after f.i. a power outage all network services have to be up
# for the bind to succeed.
while(connected == False & retries <= maxConnRetries):
    # Create a datagram socket and Bind to address and ip
    try:
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((localIP, localPort))
        connected = True
    except Exception as e:
        logger.error('Create/bind Socket Error: ' + str(e) + ' Host:' + str(localIP) + ' Port:' + str(localPort) + '. Will retry ' + str(maxConnRetries - retries) + ' more times...')
        retries = retries + 1
        if(retries == maxConnRetries):
            logger.error('I give up. Socket bind failed. Omniklogger not started!')
            exit(1)
        else:
            time.sleep(60)
    

logger.info("Omniklogger up and listening on {0} on port {1} with root loglevel: {2}".format(localIP, localPort, logging.getLevelName(logger.level)))
if logger.hasHandlers():
    logger.info("The root logger has the following handlers: {0}".format(logger.handlers))
logger.info('We are listening for UDP messages from an Inverter with serial: {0}'.format(serial))

# Listen for incoming datagrams
while(True):
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(1024)
    except Exception as e:
        logger.error('Recvfrom Socket Error: ' + str(e))
        continue
    
    msgCount = msgCount + 1
    
    msg = InverterMsg.InverterMsg(bytesAddressPair[0])
    sender = bytesAddressPair[1]

    logger.debug("Message from {0} received. Message length: {1}".format(sender, len(msg.raw_message)))
    logger.debug("msg.status: {0} msg.aknowledge: {1} msg.id: {2} serial: {3}".format(msg.status, msg.aknowledge, msg.id, serial))
    
    if msg.isNoInverterData:
        msgErrorCount = msgErrorCount + 1
        logger.error('Inverter says NO INVERTER DATA. Message:')
        logger.error(msg.dump())

    elif msg.isAknowledgement:
        msgAknowledgeCount = msgAknowledgeCount + 1
        logger.debug('Aknowledgement message received from Inverter: DATA SEND IS OK')
        
    elif msg.isUnknownLoggerMessage:
        logger.debug('Unknown logger message received from logger with firmware version: {0}'.format(msg.firmware_logger))
        
    elif msg.isDataMessage(serial):
        logger.debug("Received data from Inverter with serial: {0}".format(msg.id))
        
        for plugin in PluginBase.plugins:
            logger.debug('Forwarding received data to plugin: ' + plugin.__module__)
            plugin.process_message(msg, logger, config)

        pluginRuns = pluginRuns + 1      
        
    else:
        msgErrorCount = msgErrorCount + 1
        logger.error('Unknown Message Status or message from unknown Inverter serial received')
        logger.error(msg.dump())

    # Periodically log some stats so we know we are still running.
    # 240 is about once a day (10*(60/5)*2).
    # TODO: Change the trigger for logging this to date shift 
    if msgCount % 240 == 0:
        logger.info('Still alive. Total Messages received so far: {0} from which {1} were Error messages and {2} were Aknowledge messages. The plugin(s) were run {3} times.'.format(msgCount, msgErrorCount, msgAknowledgeCount, pluginRuns))

logger.info("Omniklogger stopped.")