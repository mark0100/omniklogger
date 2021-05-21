import PluginLoader


class InfoOutput(PluginLoader.PluginBase):
    """Outputs the version info data from the Omnik inverter to stdout"""

    def process_message(msg, logger, config):
        """Output the information from the inverter to stdout.

        Args:
            msg (InverterMsg.InverterMsg): Message to process
        """

        serial = config.get('inverter', 'serial')

        if msg.status == b'NO INVERTER DATA':
            logger.error('Inverter Status Fault. Message:')
            msg.dump()
            
        elif msg.aknowledge == b'DATA SEND IS OK':
            logger.debug('Aknowledgement message received: DATA SEND IS OK')
                
        elif msg.id == serial:

            print "Inverter serial number: {}".format(msg.id)
            print "Firmware version (main): {}".format(msg.firmware_main)
            print "Firmware version (slave): {}".format(msg.firmware_slave)

        else:
            logger.error('Unknown message received - Aborting. Message:')
            msg.dump()

