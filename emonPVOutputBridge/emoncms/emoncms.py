import http.client
import logging
import socket


class Emoncms(object):
    def __init__(self, config):
        # Logging
        self.log = logging.getLogger('root')

        # Settings for EmonCMS
        self.apiKey = config['Emoncms']['apikey']
        self.host = config['Emoncms']['host']
        self.ssl = config['Emoncms']['ssl']
        self.basePath = config['Emoncms']['path']
        self.consumptionFeedID = config['Emoncms']['consumptionfeedid']
        self.generationFeedID = config['Emoncms']['generationfeedid']
        self.voltageFeedID = config['Emoncms']['voltagefeedid']

    def getConsumptionEnergy(self):
        value = self.connectAndRetreive(self.consumptionFeedID)
        if type(value) == float:
            consumption = value * 1000
            self.log.debug('Consumption:  %.2f Wh' % consumption)
            return consumption
        else:
            return value

    def getGenerationEnergy(self):
        value = self.connectAndRetreive(self.generationFeedID)
        if type(value) == float:
            generation = value * 1000
            self.log.debug('Generation: %.2f Wh' % generation)
            return generation
        else:
            return value

    def getVoltage(self):
        value = self.connectAndRetreive(self.voltageFeedID)
        if type(value) == float:
            voltage = int(value)
            self.log.debug("Voltage: %i V" % voltage)
            return voltage
        else:
            return value

    def connectAndRetreive(self, feed) -> float:
        """
        Connect to emoncms with the host defined in config file.
        If a feed cannot be found or connection is impossible, zero is returned as value
        """
        try:
            url = self.basePath + '/feed/value.json?id=%i&apikey=%s' % (feed, self.apiKey)
            if self.ssl:
                connection = http.client.HTTPSConnection(self.host, timeout=5)
            else:
                connection = http.client.HTTPConnection(self.host, timeout=5)
            connection.request("GET", url)
            # Get the response and strip quote
            data = connection.getresponse().read().decode("utf-8")
            self.log.debug("Data received: %s" % data)
            value = float(data);
        except (http.client.HTTPException, socket.error, socket.gaierror):
            self.log.error("Unexpected error when connecting to EmonCMS")
            value = False
        except ValueError as e:
            self.log.error("Cannot retreive feed data, returning 0.0. Error -> " + e.args[0])
            value = False
        return value
