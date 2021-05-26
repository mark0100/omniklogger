# omniklogger
=====
Omniklogger is a python application for reading data from a Omniksol Solar
inverter, equipped with a wifi module, and logging this data so you can monitor 
your solarpanel installation.
The data can be logged to multiple destinations. A destination can be a
local database (mysql), CSV file, the console and/or to PVoutput.org.
PVoutput.org is a free and online solarpanel logging website.

The application is implemented as a Listener for UDP data messages send by the
Omnik solar Inverter. Your Omnik Inverter should be configured so that it will
send the UDP data messages to the system and port where omniklogger is listening.
See the Remote Server Settings in your Omnik Inverter configuration to add the
server where omniklogger is listening.

I am running omniklogger on a linux system as a Systemd service. I have included
a omniklogger-template.service file which you can use if you also want to run it
this way.
If you are on Windows or any other platform you have to provide your own script to
run the application as a service or recurring task.
   
## Installation and Setup
* Install Python 3.6 or higher
* Git clone the omniklogger source with
  `git clone https://github.com/mark0100/omniklogger.git`
* Add the system and port where onmniklogger will be listening, to the Remote Server
  Settings in your Omnik Inverter configuration.
* If you want to log to Pvoutput.org create an account for the website and lookup
  your apikey at http://pvoutput.org/account.jsp

## Configuring omniklogger
* Copy the config-template.ini to config.ini and change the settings in the new
  file as required.
* Do the same for the logging-template.ini (copy to logging.ini) and
  omniklogger-template.service (copy to omniklogger.service)
  
## Testing omniklogger
* Set only the 'ConsoleOutput' plugin in config.ini and set the logging level
  to DEBUG in logging.ini. 
* Now start the application with 'python omniklogger.py' from the commandline.
  If all is well you  will see the data messages scroll by every 5 minutes or so as
  they are received from your Inverter.
  If you see any configuration errors fix them.

## Running omniklogger
* Change the output plugin in config.ini to your desired destination(s) and set the
  logging level to INFO in logging.ini. Restart omniklogger.py.
* To create a linux SystemD service and starting the service follow the ToDo list in
  omniklogger.service
  
## A word of gratitude
Thanks to Wouterrr on github (https://github.com/Woutrrr/Omnik-Data-Logger.git) for
figuring out the Omnik message structure (InverterMsg.py) and the plugable outputs.
 

