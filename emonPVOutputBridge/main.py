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
from apscheduler.scheduler import Scheduler

scheduler = Scheduler()
logging.basicConfig(format='%(asctime)s %(name)s - %(levelname)s: %(message)s', level=logging.DEBUG)

debug = True
config = None

# Store previous values to calculate energy values
prev_consumption = 0
prev_generation = 0

class Loader(object):

    def __init__(self):
        # Logging
        self.log = logging.getLogger(__name__)

        # Get options via arg
        self.options = sys.argv[1:]

        # Load settings
        self.config = configparser.ConfigParser()
        config_file = 'config.ini'
        if not self.config.read(config_file):
            self.log.critical('Config file: ' + config_file + ' not found!')
            sys.exit(1)

    def addSignals(self):
        signal.signal(signal.SIGINT, self.onExitSignal)
        signal.signal(signal.SIGTERM, lambda signum, stack_frame: sys.exit(1))

    def onExitSignal(self, signal, frame):
        self.log.info('Exit received with signal ' + str(signal) + ', cleanup')
        sys.exit(signal)

    def run(self):
        self.addSignals()

        from core.helpers import configAsDict
        main(configAsDict(self.config))


def main(cfg):
    global config
    config = cfg
    scheduler.start()
    setInitialValues(config)
    while 1:
        time.sleep(1)

@scheduler.cron_schedule(minute='*/1')
#@scheduler.interval_schedule(seconds=10)
def getEnergy():
    global prev_generation, prev_consumption
    from core.csvwriter import writeCSV
    # Create objects for handling PVOutput and EmonCMS
    ecms = emoncms.Emoncms(config)
    pvo = pvoutput.PVOutput(config)

    # Get data from EmonCMS
    con = ecms.getConsumptionEnergy()
    gen = ecms.getGenerationEnergy()
    vol = ecms.getVoltage()

    # Post data to PVOutput and write CSV
    pvo.postPower(con - prev_consumption, gen - prev_generation, vol)
    writeCSV(con - prev_consumption, gen - prev_generation, vol, config)

    # Update prev variables to current values
    prev_consumption = con
    prev_generation = gen


# Set initial values for calculation of energy
def setInitialValues(config):
    global prev_consumption, prev_generation
    ecms = emoncms.Emoncms(config)
    prev_consumption = ecms.getConsumptionEnergy()
    prev_generation = ecms.getGenerationEnergy()

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
        raise