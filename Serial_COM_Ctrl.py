import serial.tools.list_ports

class SerialCtrl:
    def __init__(self):
        pass

    def getComPorts(self):
        """
        Get a list of available COM ports.
        Returns:
            list: A list of available COM ports.
        """
        comports_obj = serial.tools.list_ports.comports()
        devices = [port.device for port in comports_obj] # device is the name of the port, e.g., 'COM3'
        devices.insert(0, "-")
        return devices

if __name__ == "__main__":
    SerialCtrl() #deactivate just to avoid running the code when this file is imported , for safety