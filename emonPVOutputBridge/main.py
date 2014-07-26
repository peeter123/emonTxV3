#! /usr/bin/env python3
__author__ = 'peeter123'

import logging
import time
import signal
import sys
import traceback
import argparse
import os
import shutil

from apscheduler.scheduler import Scheduler

import emoncms.emoncms as emoncms
import pvoutput.pvoutput as pvoutput
import core.log as log


class emonPVOutputBridge(object):

    from core.helpers import getGitRevisionShortHash
    __version__ = getGitRevisionShortHash().decode()[0:-1]

    def __init__(self, config):
        # Scheduler
        self.scheduler = Scheduler()

        # Logging
        self.log = logging.getLogger('root')

        # Config
        self.config = config

        # Set log level according to debug config parameter
        if not self.config['System']['debug']:
            self.log.setLevel(logging.INFO)

        # Store previous values to calculate energy values
        self.inital_read = False
        self.prev_consumption = 0
        self.prev_generation = 0

    def addSignals(self):
        signal.signal(signal.SIGINT, self.onExitSignal)
        signal.signal(signal.SIGTERM, lambda signum, stack_frame: sys.exit(1))

    def onExitSignal(self, signal, frame):
        from core.helpers import signalToName
        self.log.warning('Exit received with signal ' + signalToName(signal) + ', cleanup')
        self.scheduler.shutdown()
        logging.shutdown()
        sys.exit(signal)

    def run(self):
        self.addSignals()

        # Add getEnergy as a cronjob, scheduled every 'interval' minute
        interval = '*/%i' % self.config['PVOutput']['interval']
        self.scheduler.add_cron_job(self.getEnergy, minute=interval)
        self.main()

    def main(self):
        self.scheduler.start()
        self.setInitialValues()
        while 1:
            time.sleep(1)

    def getEnergy(self):
        from core.csvwriter import writeCSV
        # Create objects for handling PVOutput and EmonCMS
        ecms = emoncms.Emoncms(self.config)
        pvo = pvoutput.PVOutput(self.config)

        # Get data from EmonCMS
        con = ecms.getConsumptionEnergy()
        gen = ecms.getGenerationEnergy()
        vol = ecms.getVoltage()

        if con and gen and vol and self.inital_read:
            # Post data to PVOutput and write CSV
            pvo.postPower(con - self.prev_consumption, gen - self.prev_generation, vol)
            writeCSV(con - self.prev_consumption, gen - self.prev_generation, vol, self.config)

            # Update prev variables to current values
            self.prev_consumption = con
            self.prev_generation = gen
        elif not self.inital_read:
            self.log.warning("Initial values not read, do that first before posting tom PVOutput.")
            self.setInitialValues()
        else:
            self.log.warning("No data received from emoncms, not posting to PVOutput. "
                             "Check your settings and internet connection.")

    # Set initial values for calculation of energy
    def setInitialValues(self):
        self.log.info("Reading initial values from emoncms")
        ecms = emoncms.Emoncms(self.config)

        con = ecms.getConsumptionEnergy()
        gen = ecms.getGenerationEnergy()

        if con and gen:
            self.inital_read = True
            self.prev_consumption = con
            self.prev_generation = gen
        else:
            self.log.warning("No data received from emoncms. "
                             "Check your settings and internet connection.")

if __name__ == '__main__':

    # Command line arguments parser
    parser = argparse.ArgumentParser(description='EmonCMS to PVOutput bridge')

    # Configuration file
    parser.add_argument("--config-file", action="store",
                        help='Configuration file (default: config.ini)', default=sys.path[0]+'/config.ini')
    # Log file
    parser.add_argument('--logfile', action='store', type=argparse.FileType('a'),
                        help='Log file (default: log to Standard out stream STDOUT)')
    # Show version
    parser.add_argument('-v', '--version', action='store_true',
                        help='Display version number and exit')
    # Parse arguments
    args = parser.parse_args()

    # Display version number and exit
    if args.version:
        print('emonPVOutputBridge version %s' % emonPVOutputBridge.__version__)
        sys.exit()

    # Logging configuration
    if args.logfile is None:
        # If no path was specified, everything goes to sys.stdout
        logger = log.setupCustomStdoutLogger('root')
    else:
        # Otherwise, rotating logging over two 5 MB files
        # If logfile is supplied, argparse opens the file in append mode, this ensures it is writable
        # Close the file for now and get its path
        args.logfile.close()
        logger = log.setupCustomFileLogger('root', args.logfile.name)

    logger.info('Starting emonPVOutputBridge version %s' % emonPVOutputBridge.__version__)

    # Parse and validate config
    from core.config import createConfigFromFile
    if os.path.isfile(args.config_file):
        logger.info('Read config from %s' % args.config_file)
        config = createConfigFromFile(args.config_file)
    else:
        logger.warning('Created config file from dist, please check your settings!')
        shutil.copy2('config.dist.ini', 'config.ini')
        config = createConfigFromFile(args.config_file)

    epvb = None
    try:
        epvb = emonPVOutputBridge(config)
        epvb.run()
    except SystemExit:
        raise
    except:
        try:
            # if this fails we will have two tracebacks
            # one for failing to log, and one for the exception that got us here.
            if epvb:
                epvb.log.critical(traceback.format_exc())
            else:
                print(traceback.format_exc())
        except:
            print(traceback.format_exc())