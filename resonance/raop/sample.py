import sys
import logging

logger = logging.getLogger(__name__)


def identify_renderers() -> int:
    """
    Execute 'squeeze2raop-macos-arm64-static' library with –i argument
    to store the config file in resonance/raop/conf/raop-config.xml

    From Squeeze2Raop – AirPlay bridge - User Guide:

    3.2    Identify Your AirPlay Renderers
        Follow these steps:

        Turn on all the renderers you might ever want to use and make sure they are connected to your local network.
        Run the squeeze2raop program from a command line.  Wait for about 1 minute.
        Type ‘save config.xml’
        Type exit
        -or- (preferred method)

        Run the “squeeze2raop –i config.xml” from a command line
        After less than 1 minute, the program exits

    Note:
        the invoked file in lib must be flagged as executable
        `chmod u+x squeeze2raop-macos-arm64-static`
    """
    lib_name = 'squeeze2raop-macos-arm64-static'
    import subprocess
    value = subprocess.check_output([f'resonance/raop/lib/{lib_name}', '-i', 'resonance/raop/conf/raop-config.xml'])
    logger.debug(f'{lib_name} returned {value}')
    return int.from_bytes(value)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(identify_renderers())
