"""This module wraps the HTTP requests for the ASCOM Alpaca API into pythonic classes with methods.

Attributes:
    DEFAULT_API_VERSION (int): Default Alpaca API spec to use if none is specified when needed.

"""
import requests


DEFAULT_API_VERSION = 1


class Device:
    """Common methods across all ASCOM Alpaca devices.

    Attributes:
        address (str): Domain name or IP address of Alpaca server.
            Can also specify port number if needed.
        device_type (str): One of the recognised ASCOM device types
            e.g. telescope (must be lower case).
        device_number (int): Zero based device number as set on the server (0 to 4294967295).
        protocall (str): Protocall used to communicate with Alpaca server.
        api_version (int): Alpaca API version.
        base_url (str): Basic URL to easily append with commands.

    """

    def __init__(self, address, device_type, device_number, protocall, api_version):
        """Initialize Device object."""
        self.address = address
        self.device_type = device_type
        self.device_number = device_number
        self.api_version = api_version
        self.base_url = "%s://%s/api/v%d/%s/%d" % (
            protocall,
            address,
            api_version,
            device_type,
            device_number,
        )

    def action(self, action, *args):
        """Access functionality beyond the built-in capabilities of the ASCOM device interfaces.
        
        Args:
            action: A well known name that represents the action to be carried out.
            *args: List of required parameters or empty if none are required.

        """
        return self._put("action", {"Action": action, "Parameters": args})["Value"]

    def commandblind(self, command, raw):
        """Transmit an arbitrary string to the device and does not wait for a response.

        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to transmission.

        """
        return self._put("commandblind", {"Command": command, "Raw": raw})["Value"]

    def commandbool(self, command, raw):
        """Transmit an arbitrary string to the device and wait for a boolean response.
        
        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to transmission.

        """
        return self._put("commandbool", {"Command": command, "Raw": raw})["Value"]

    def commandstring(self, command, raw):
        """Transmit an arbitrary string to the device and wait for a string response.

        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to transmission.

        """
        return self._put("commandstring", {"Command": command, "Raw": raw})["Value"]

    def connected(self, connected=None):
        """Retrieve or set the connected state of the device.

        Args:
            connected (bool): Set True to connect to device hardware.
                Set False to disconnect from device hardware.
                Set None to get connected state (default).
        
        """
        if connected == None:
            return self._get("connected")
        else:
            self._put("connected", {"Connected": connected})

    def description(self):
        """Get description of the device."""
        return self._get("name")

    def driverinfo(self):
        """Get information of the device."""
        return [i.strip() for i in self._get("driverinfo").split(",")]

    def driverversion(self):
        """Get string containing only the major and minor version of the driver."""
        return self._get("driverversion")

    def interfaceversion(self):
        """ASCOM Device interface version number that this device supports."""
        return self._get("interfaceversion")

    def name(self):
        """Get name of the device."""
        return self._get("name")

    def supportedactions(self):
        """Get list of action names supported by this driver."""
        return self._get("supportedactions")

    def _get(self, attribute):
        """Send an HTTP GET request to an Alpaca server and check response for errors.

        Args:
            attribute (str): Attribute to get from server.
        
        """
        response = requests.get("%s/%s" % (self.base_url, attribute))
        self.__check_error(response)
        return response.json()["Value"]

    def _put(self, attribute, data={}):
        """Send an HTTP PUT request to an Alpaca server and check response for errors.

        Args:
            attribute (str): Attribute to put to server.
            data: Data to send with request.
        
        """
        response = requests.put("%s/%s" % (self.base_url, attribute), data=data)
        self.__check_error(response)
        return response.json()

    def __check_error(self, response):
        """Check response from Alpaca server for Errors.

        Args:
            response (Response): Response from Alpaca server to check.

        """
        if response.json()["ErrorNumber"] != 0:
            raise Exception(
                "Error %d: %s"
                % (response.json()["ErrorNumber"], response.json()["ErrorMessage"])
            )
        elif response.status_code == 400 or response.status_code == 500:
            raise Exception(response.json()["Value"])
