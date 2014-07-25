import time
import http.client
import logging


class PVOutput(object):
    def __init__(self, config):
        # Logging
        self.log = logging.getLogger(__name__)

        # Api key and system id
        self.apiKey = config['PVOutput']['apikey']
        self.sysId = config['PVOutput']['sysid']
        self.interval = config['PVOutput']['interval']

    def postPower(self, consumption, generation, voltage):
        current_time = time.strptime(time.ctime(time.time()))
        d = time.strftime('%Y%m%d', current_time)
        t = time.strftime('%H:%M', current_time)
        power_generation = generation / (int(self.interval)/60)
        power_consumption = consumption / (int(self.interval)/60)
        self.log.debug("Power generation: " + '%.2f' % power_generation + " W")
        self.log.debug("Power consumption: " + '%.2f' % power_consumption + " W")

        url = "/service/r2/addstatus.jsp?key=%s&sid=%s&d=%s&t=%s&v2=%i&v4=%i&v6=%i" % \
              (self.apiKey, self.sysId, d, t, int(power_generation), int(power_consumption), int(voltage))

        try:
            self.log.debug("Connecting to pvoutput.org" + url)
            connection = http.client.HTTPConnection("pvoutput.org")
            connection.request("GET", url)
            response = connection.getresponse()
            self.log.info("Adding to PVOutput: %s - %s" % (d, t))
            self.log.info("                    %.2f Wh generated (%.2f W)" % (generation, power_generation))
            self.log.info("                    %.2f Wh consumed (%.2f W)" % (consumption, power_consumption))
            self.log.info("                    %i V" % voltage)
            self.log.info("PVOutput response: " + response.read().decode("utf-8"))
        except http.client.HTTPException:
            self.log.error("Unexpected error when connecting to PVOutput")