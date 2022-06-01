import PluginLoader


class RawMessageOutput(PluginLoader.PluginBase):
    """Outputs the raw message from the Omnik inverter to stdout"""

    def process_message(msg, logger, config):
        """Output the raw message from the inverter to stdout.

        Args:
            msg (InverterMsg.InverterMsg): Message to process
        """

        print(msg.dump())

