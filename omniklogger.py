#!/usr/bin/python
import socket
import logging
import logging.handlers
from logging.config import fileConfig
import InverterMsg  # Import the Msg handler
import datetime
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

config = None
logger = None
msgCount = 0
msgErrorCount = 0
msgAknowledgeCount = 0
pluginRunTime = 0

# Load the setting
configFile = expandPath('config.ini')

config = configparser.RawConfigParser()
config.read(configFile)

# Load the logging settings
fileConfig(expandPath('logging.ini'))
logger = logging.getLogger()

logger.info("Starting omniklogger") 

# Load output plugins
# Prepare path for plugin loading
sys.path.append(expandPath('outputs'))

# TODO: Howto pass the config and logger vars to the plugins on creation
# instead of passing them in the process_message function?
#PluginBase.config = config
#PluginBase.logger = logger

enabled_plugins = config.get('general', 'enabled_plugins').split(',')
for plugin_name in enabled_plugins:
    plugin_name = plugin_name.strip()
    logger.info('Importing output plugin: ' + plugin_name)
    __import__(plugin_name)

serial = str.encode(config.get('inverter', 'serial'))

localIP = config.get('UDPListener', 'localIP')
localPort = int(config.get('UDPListener', 'localPort'))

# Create a datagram socket and Bind to address and ip
try:
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
except Exception as e:
    logger.error('Create/bind Socket Error: ' + e)
    sys.exit(1)
    
# TODO: How to get the loglevel of the filehandler here instead of the root logger
logger.info("Omniklogger up and listening on {0} on port {1} with loglevel: {2}".format(localIP, localPort, logging.getLevelName(logger.level)))
logger.info('We are listening for UDP messages from an Inverter with serial: {0}'.format(serial))

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(1024)

    msgCount = msgCount + 1
    
    #raw_msg = bytesAddressPair[0]
    msg = InverterMsg.InverterMsg(bytesAddressPair[0])
    sender = bytesAddressPair[1]

    logger.debug("{0}: Message from: {1}".format(datetime.datetime.now(), sender))
    logger.debug("msg.status: {0} msg.aknowledge: {1} msg.id: {2} serial: {3}".format(msg.status, msg.aknowledge, msg.id, serial))
    
    if msg.isNoInverterData:
        msgErrorCount = msgErrorCount + 1
        logger.error('Inverter says NO INVERTER DATA. Message:')
        logger.error(msg.dump())

    elif msg.isAknowledgement:
        msgAknowledgeCount = msgAknowledgeCount + 1
        logger.debug('Aknowledgement message received from Inverter: DATA SEND IS OK')

    elif msg.isDataMessage(serial):
        logger.debug("Received data from Inverter with serial: {0}".format(msg.id))
        
        for plugin in PluginBase.plugins:
        	#TODO How to get the plugin name?
            logger.debug('Running plugin: ' + plugin.__class__.__name__)
            plugin.process_message(msg, logger, config)

        pluginRunTime = pluginRunTime + 1      
        
    else:
        msgErrorCount = msgErrorCount + 1
        logger.error('Unknown Message Status or message from unknown Inverter serial received')
        logger.error(msg.dump())

    # Periodically log some stats so we know we are still running fine by looking at the log.
    # 192 is about once a day (8*(60/5)*2).
    if msgCount % 192 == 0:
        logger.info('Still alive. Total Messages received so far: {0} from which {1} were Error messages and {2} were Aknowledge messages. The plugin(s) were run {3} times.'.format(msgCount, msgErrorCount, msgAknowledgeCount, pluginRunTime))

