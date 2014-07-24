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

    def postPower(self, consumption, generation, voltage):
        current_time = time.strptime(time.ctime(time.time()))
        d = time.strftime('%Y%m%d', current_time)
        t = time.strftime('%H:%M', current_time)
        power_generation = generation / (1/60)
        power_consumption = consumption / (1/60)

        print('%.2f'%power_generation + ' & ' + '%.2f'%power_consumption)

        url = "/service/r2/addstatus.jsp?key=%s&sid=%s&d=%s&t=%s&v1=%.2f&v3=%.2f&v6=%i" % (self.apiKey, self.sysId, d, t, generation, consumption, int(voltage))

        # try:
        #     connection = http.client.HTTPConnection("pvoutput.org")
        #     connection.request("GET", url)
        #     response = connection.getresponse()
        #     self.log.info("Adding: %s - %s" % (d, t))
        #     self.log.info(response.read().decode("utf-8"))
        # except:
        #     self.log.error("Unexpected error when connecting to PVOutput")