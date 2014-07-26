__author__ = 'vm'
import logging
import sys
import configobj
import validate


cfg = """
[System]
storecsv = boolean(default=False)
csvpath = string()
debug = boolean(default=False)
[Emoncms]
apikey = string()
host = string()
path = string()
consumptionfeedid = integer()
generationfeedid = integer()
voltagefeedid = integer()
[PVOutput]
apikey = string()
sysid = integer()
interval = integer(min=1, max=59, default=5)
upload = boolean(default=True)
"""

log = logging.getLogger('root')


def createConfigFromFile(path) -> configobj.ConfigObj:
    """
    Create a config from file using a configspec and validate against the configspec
    If an error is found the error is reported and the program exits
    """
    spec = cfg.split("\n")
    config = configobj.ConfigObj(path, configspec=spec)
    validator = validate.Validator()
    results = config.validate(validator, preserve_errors=True)

    for entry in configobj.flatten_errors(config, results):
        [sectionList, key, error] = entry
        if not error:
            msg = "The parameter %s was not in the config file\n" % key
            msg += "Please check to make sure this parameter is present and there are no mis-spellings."
            log.critical(msg)
            sys.exit(1)

        if key is not None and isinstance(error, validate.VdtTypeError):
            msg = ("The parameter '%s' in '%s' is wrong, " + error.args[0]) % (key, sectionList[0])
            log.critical(msg)
            sys.exit(1)

    return config