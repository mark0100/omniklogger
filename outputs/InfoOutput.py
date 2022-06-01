import PluginLoader


class InfoOutput(PluginLoader.PluginBase):
    """Outputs the version info data from the Omnik inverter to stdout"""

    def process_message(msg, logger, config):
        """Output the information from the inverter to stdout.

        Args:
            msg (InverterMsg.InverterMsg): Message to process
        """

        serial = str.encode(config.get('inverter', 'serial'))
        
        if msg.isDataMessage(serial):
            print ("Inverter serial number: {}".format(msg.id))
            print ("Firmware version (main): {}".format(msg.firmware_main))
            print ("Firmware version (slave): {}".format(msg.firmware_slave))

