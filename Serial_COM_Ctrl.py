import time
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
    
    def SerialOpen(self, ComGUI):
        PORT = ComGUI.clicked_com.get()
        BAUD = ComGUI.clicked_bd.get()

        try:
            if not hasattr(self, 'ser') or self.ser is None or not self.ser.is_open:
                self.ser = serial.Serial(
                    port=PORT, 
                    baudrate=int(BAUD), 
                    timeout=0.1,
                    )
            print("Serial port opened.")
            self.ser.status = True
        except Exception as e:
            print(f"Failed to open serial port: {e}")
            self.ser.status = False    

    def SerialClose(self, ComGUI):
        '''
        Method used to close the UART communication
        '''
        try:
            self.ser.is_open
            self.ser.close()
            self.ser.status = False
        except:
            self.ser.status = False
  

if __name__ == "__main__":
    SerialCtrl() #deactivate just to avoid running the code when this file is imported , for safety