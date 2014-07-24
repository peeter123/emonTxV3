import time
import json
import http.client
import logging


class Emoncms(object):
    def __init__(self, config):
        # Logging
        self.log = logging.getLogger(__name__)

        # Api key for EmonCMS
        self.apiKey = config['Emoncms']['apikey']
        self.host = config['Emoncms']['host']
        self.basePath = config['Emoncms']['path']
        self.consumptionFeedID = config['Emoncms']['consumptionfeedid']
        self.generationFeedID = config['Emoncms']['generationfeedid']
        self.voltageFeedID = config['Emoncms']['voltagefeedid']

    def getConsumptionEnergy(self):
        try:
            connection = http.client.HTTPConnection(self.host, timeout=5)
            url = self.basePath + '/feed/value.json?id=' + self.consumptionFeedID + '&apikey=' + self.apiKey
            connection.request("GET", url)
            # Get the response and strip quote
            consumption = float(connection.getresponse().read().decode("utf-8")[1:-1]) * 1000
            self.log.debug("Consumption: " + '%.2f' % consumption + " Wh")
            return consumption
        except http.client.HTTPException:
            self.log.error("Unexpected HTTP error when connecting to EmonCMS")

    def getGenerationEnergy(self):
        try:
            connection = http.client.HTTPConnection(self.host, timeout=5)
            url = self.basePath + '/feed/value.json?id=' + self.generationFeedID + '&apikey=' + self.apiKey
            connection.request("GET", url)
            # Get the response and strip quote
            generation = float(connection.getresponse().read().decode("utf-8")[1:-1]) * 1000
            self.log.debug("Generation: " + '%.2f' % generation + " Wh")
            return generation
        except http.client.HTTPException:
            self.log.error("Unexpected HTTP error when connecting to EmonCMS")

    def getVoltage(self):
        try:
            connection = http.client.HTTPConnection(self.host, timeout=5)
            url = self.basePath + '/feed/value.json?id=' + self.voltageFeedID + '&apikey=' + self.apiKey
            connection.request("GET", url)
            # Get the response and strip quote
            voltage = connection.getresponse().read().decode("utf-8")[1:-1]
            self.log.debug("Voltage: " + voltage + " V")
            return voltage
        except http.client.HTTPException:
            self.log.error("Unexpected HTTP error when connecting to EmonCMS")