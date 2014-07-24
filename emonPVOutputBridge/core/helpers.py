import configparser
import struct


def configAsDict(config: configparser.ConfigParser) -> dict:
    """
    Converts a ConfigParser object into a dictionary.

    The resulting dictionary has sections as keys which point to a dict of the
    sections options as key => value pairs.
    """
    the_dict = {}
    for section in config.sections():
        the_dict[section] = {}
        for key, val in config.items(section):
            the_dict[section][key] = val
    return the_dict

def bytesToInt(b1, b2):
    return struct.unpack( "h", bytes([int(b1), int(b2)]))[0]