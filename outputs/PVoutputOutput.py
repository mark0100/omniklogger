import PluginLoader
import datetime
import urllib.parse
import urllib.request


class PVoutputOutput(PluginLoader.PluginBase):
    """Sends the data from the Omnik inverter to PVoutput.org"""

    def process_message(msg, logger, config):
        """Send the information from the inverter to PVoutput.org.

        Args:
            msg (InverterMsg.InverterMsg): Message to process

        """
        now = datetime.datetime.now()
        response = None

        logger.debug('PVOutputoutput: Uploading to PVoutput')

        url = "http://pvoutput.org/service/r2/addstatus.jsp"

        if config.getboolean('inverter', 'use_temperature'):
            get_data = {
                'key': config.get('pvout', 'apikey'),
                'sid': config.get('pvout', 'sysid'),
                'd': now.strftime('%Y%m%d'),
                't': now.strftime('%H:%M'),
                'v1': msg.e_today * 1000,
                'v2': msg.p_ac(1),
                'v5': msg.temperature,
                'v6': msg.v_ac(1)
            }
        else:
            get_data = {
                'key': config.get('pvout', 'apikey'),
                'sid': config.get('pvout', 'sysid'),
                'd': now.strftime('%Y%m%d'),
                't': now.strftime('%H:%M'),
                'v1': msg.e_today * 1000,
                'v2': msg.p_ac(1),
                'v6': msg.v_pv(1)
            }

        get_data_encoded = urllib.parse.urlencode(get_data)

        request_object = urllib.request.Request(url + '?' + get_data_encoded)

        logger.debug('PVoutputOutput request: {0}'.format(url + '?' + get_data_encoded))
                        
        try:
            response = urllib.request.urlopen(request_object)
        except Exception as e:
            logger.error('PVoutputOutput Error: ' + str(e))
            logger.error('PVoutputOutput request was: {0}'.format(url + '?' + get_data_encoded))

        if response is not None:
            logger.debug('PVoutputOutput: response from PVOutput site: {0}'.format(response.read()))
        else:
            logger.error('PVoutputOutput: No response from PVOutput site. Aborting PVOutputoutput...')
                
