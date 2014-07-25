__author__ = 'vm'
import time
import os
import csv
import sys
import logging
from distutils.util import strtobool

# Logging
log = logging.getLogger('root')


def writeCSV(consumption, generation, voltage, config):
    if strtobool(config['System']['storecsv']):
        d = time.strftime('%Y%m%d')
        t = time.strftime('%H:%M')
        path = config['System']['csvpath']
        file = path + "%s.csv" % d

        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError:
                log.critical('Cannot create csv directory')
                sys.exit(1)

        if not os.path.exists(file):
            with open(file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Date', 'Time', 'Consumption (Wh)', 'Generation (Wh)', 'Voltage (V)'])

        with open(file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([d, t, consumption, generation, voltage])
            log.debug('Writerow with contents: ' + d + ', ' + t + ', ' + '%.2f' % consumption +
                      ', ' + '%.2f' % generation + ', ' + '%i' % voltage + ' to ' + file)