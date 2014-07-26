import configparser
import struct
import signal

def signalToName(signal_number) -> str:
    SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n) for n in dir(signal) if n.startswith('SIG') and '_' not in n )
    return SIGNALS_TO_NAMES_DICT.get(signal_number, "UNNAMED: %d" % signal_number)


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


def getGitRevisionShortHash() -> bytes:
    import subprocess
    versionHash = None
    try:
        versionHash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
    except (subprocess.CalledProcessError, FileNotFoundError):
        versionHash = 'Unknown\n'.encode()
    return versionHash