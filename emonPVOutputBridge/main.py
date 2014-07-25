#! /usr/bin/env python3
__author__ = 'peeter123'

import logging
import time
import signal
import sys
import configparser
import traceback
import emoncms.emoncms as emoncms
import pvoutput.pvoutput as pvoutput
import core.log as log
from distutils.util import strtobool
from apscheduler.scheduler import Scheduler


class Loader(object):

    def __init__(self):
        # Scheduler
        self.scheduler = Scheduler()

        # Logging
        self.log = log.setupCustomLogger('root')

        # Get options via arg
        self.options = sys.argv[1:]

        # Load settings
        from core.helpers import configAsDict
        cp = configparser.ConfigParser()
        config_file = 'config.ini'
        if not cp.read(config_file):
            self.log.critical('Config file: ' + config_file + ' not found!')
            sys.exit(1)
        self.config = configAsDict(cp)

        # Set log level according to debug config parameter
        if not strtobool(self.config['System']['debug']):
            logging.getLogger('root').setLevel(logging.INFO)

        # Store previous values to calculate energy values
        self.prev_consumption = 0
        self.prev_generation = 0

    def addSignals(self):
        signal.signal(signal.SIGINT, self.onExitSignal)
        signal.signal(signal.SIGTERM, lambda signum, stack_frame: sys.exit(1))

    def onExitSignal(self, signal, frame):
        self.log.warning('Exit received with signal ' + str(signal) + ', cleanup')
        self.scheduler.shutdown()
        sys.exit(signal)

    def run(self):
        self.addSignals()

        # Add getEnergy as a cronjob, scheduled every 'interval' minute
        interval = '*/' + self.config['PVOutput']['interval']
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
        con = float(ecms.getConsumptionEnergy())
        gen = float(ecms.getGenerationEnergy())
        vol = int(ecms.getVoltage())

        # Post data to PVOutput and write CSV
        pvo.postPower(con - self.prev_consumption, gen - self.prev_generation, vol)
        writeCSV(con - self.prev_consumption, gen - self.prev_generation, vol, self.config)

        # Update prev variables to current values
        self.prev_consumption = con
        self.prev_generation = gen

    # Set initial values for calculation of energy
    def setInitialValues(self):
        self.log.info("Startup - reading initial values from emoncms")
        ecms = emoncms.Emoncms(self.config)
        self.prev_consumption = ecms.getConsumptionEnergy()
        self.prev_generation = ecms.getGenerationEnergy()

if __name__ == '__main__':
    l = None
    try:
        l = Loader()
        l.run()
    except SystemExit:
        raise
    except:
        try:
            # if this fails we will have two tracebacks
            # one for failing to log, and one for the exception that got us here.
            if l:
                l.log.critical(traceback.format_exc())
            else:
                print(traceback.format_exc())
        except:
            print(traceback.format_exc())