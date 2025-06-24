import threading
import time
import serial
import numpy as np
import sys

TMF882X_CHANNELS = 10
TMF882X_BINS = 128
TMF882X_SKIP_FIELDS = 3                         # skip first 3 fields
TMF882X_IDX_FIELD = (TMF882X_SKIP_FIELDS-1)
# this is the array for summing up each channel 
rawSum = [[0 for _ in range(TMF882X_BINS)] for _ in range(TMF882X_CHANNELS)]
eclSum = [[0 for _ in range(TMF882X_BINS)] for _ in range(TMF882X_CHANNELS)]

class DataReader(threading.Thread):
    def __init__(self, data_queue, serial_port, channel_number=5):
        super().__init__(daemon=True)
        self.data_queue = data_queue
        self.channel_number = channel_number
        self.running = True
        self.arduino = serial_port.ser #serial.Serial(port='COM3', baudrate=115200, timeout=0.1)
        self.setup_arduino()

    def setup_arduino(self):
        # give arduinto time to wakeup
        while ( True ):
            data = self.read()
            if ( len(data) > 0 ):
                print( "started receiving ... ")
                break                                           # leave waiting loop
            else:
                time.sleep( 1.0 )
                self.write( 'h' )                                    # try to get device talking
                
        self.waitForArduinoStopTalk()                                # wait for the device to stop talking
        print( "Now we can instruct the device to do something ")

        self.write( 'd' )                                            # disable device for a clean start
        self.waitForArduinoStopTalk()

        print( "Enable device and download fw ----------------------- ")
        self.write( 'E' )                                            # enable device e is for 8288, E is for 882x
        self.waitForArduinoStartTalk()                               # wait for the device to start talking
        self.waitForArduinoStopTalk()                                # wait for the device to stop talking

        # switching spad mask configuration refer to datasheet, but by defauly is 3x3 normal mode, one c turns into id=2, which is still 3x3, twice c id=3 which is 4x4, once more cycles back to 1
        # write( 'c' )                                            
        # waitForArduinoStopTalk()                                # wait for the device to stop talking
        # write( 'c' )                                            
        # waitForArduinoStopTalk()                                # wait for the device to stop talking

        # writing z 1 - 3 times will produce 3 different modes, 1 time is raw, 2 times is calibration, 3 times is raw+calibration
        print( "Dump also raw+calibration histograms ---------------- ")
        self.write( 'z' )                                            # raw histograms
        self.waitForArduinoStopTalk()                                # wait for the device to stop talking
        # write( 'z' )                                            # calibration histograms
        # waitForArduinoStopTalk()                                # wait for the device to stop talking
        # write( 'z' )                                            # raw+calibration histograms
        # waitForArduinoStopTalk()                                # wait for the device to stop talking

    def run(self):
        print( "Now start measurements ")
        self.write( 'm' )
        while self.running:
            # # Simulate a line from a TDC sensor
            # line = f"#RCo{self.channel_number}," + ",".join(str(np.random.randint(0, 100)) for _ in range(128))
            # self.data_queue.put(line)
            # # simulate data arriving every second
            # threading.Event().wait(1)
            data = self.read()
            data = data.decode('utf-8')
            data = data.replace('\r','')                    # remove unwanted \r and \n to not have them 
            data = data.replace('\n','')                    # in the CSV file as unwanted chars
            row = data.split(',')
            if ( len(row) > 0 and row[0][0] == '#'):
            # write the raw line to the csv file either #Raw or #Cal
            # csvwriter.writerow( row )                   # dump all lines that start with a hashtag
                if ( row[0] ==  '#Obj' ):
                    rowtowrite = row 
                elif ( row[0] == '#Raw' and len(row) == TMF882X_BINS+TMF882X_SKIP_FIELDS ):
                    # skip the I2C slave address field
                    idx = int(row[TMF882X_IDX_FIELD])
                    if ( idx >= 0 and idx <= 9 ):
                        for col in range(TMF882X_BINS):
                            rawSum[idx][col] = int( row[TMF882X_SKIP_FIELDS+col] )                                      # LSB is only assignement
                    elif ( idx >= 10 and idx <= 19 ):
                        idx = idx - 10
                        for col in range(TMF882X_BINS):
                            rawSum[idx][col] = rawSum[idx][col] + int(row[TMF882X_SKIP_FIELDS+col]) * 256               # mid
                    elif ( idx >= 20 and idx <= 29 ):
                        idx = idx - 20
                        for col in range(TMF882X_BINS):
                            rawSum[idx][col] = rawSum[idx][col] + int(row[TMF882X_SKIP_FIELDS+col]) * 256 * 256         # MSB
                        rowtowrite = ["#RCo"+str( idx )] + rawSum[idx]
                        # print(rowtowrite) # the row here is an array of the intensity value for each time bin, array[0] is the RCoX string, the rest is the histogram values
                        #e.g. ['#RCo9', 11, 12, 15, 13, 7, ... , 0, 0, 0]
                        if rowtowrite[0].startswith(f"#RCo{self.channel_number}"):
                            line = ','.join(map(str, rowtowrite)) + '\n'  # map str() to convert all int in the rowtowrite array to string and join them with a "," separator
                            self.data_queue.put(line)
                            threading.Event().wait(0.8)
                        
                elif ( row[0] == '#Cal' and len(row) == TMF882X_BINS+TMF882X_SKIP_FIELDS ):
                    # skip the I2C slave address field
                    idx = int(row[TMF882X_IDX_FIELD])
                    if ( idx >= 0 and idx <= 9 ):
                        for col in range(TMF882X_BINS):
                            rawSum[idx][col] = int( row[TMF882X_SKIP_FIELDS+col] )                                      # LSB is only assignement
                    elif ( idx >= 10 and idx <= 19 ):
                        idx = idx - 10
                        for col in range(TMF882X_BINS):
                            rawSum[idx][col] = rawSum[idx][col] + int(row[TMF882X_SKIP_FIELDS+col]) * 256               # mid
                    elif ( idx >= 20 and idx <= 29 ):
                        idx = idx - 20
                        for col in range(TMF882X_BINS):
                            rawSum[idx][col] = rawSum[idx][col] + int(row[TMF882X_SKIP_FIELDS+col]) * 256 * 256         # MSB
                        rowtowrite = ["#CCo"+str( idx )] + rawSum[idx]
                        if rowtowrite[0].startswith(f"#CCo{self.channel_number}"):
                            line = ','.join(map(str, rowtowrite)) + '\n'  # map str() to convert all int in the rowtowrite array to string and join them with a "," separator
                            self.data_queue.put(line)
                            threading.Event().wait(0.8)

    def stop(self):
        self.running = False 
        self.write( 's' )                                            # stop measurements
        self.waitForArduinoStopTalk()                                # wait for the device to stop talking
        
        self.write( 'd' )                                            # disable device
        self.waitForArduinoStopTalk()                                # wait for the device to stop talking

        self.arduino.close()                                         # close serial port
        print( "End of program")

    def write(self, x):
        """
        Write a single byte to the arduino
        Args:
            x (character): Must be one of the commands the arduino program understands, h,e,d,w,p,m,s,c,f,l,a,x.
        """
        self.arduino.write(bytes(x, 'utf-8'))
        time.sleep(0.05)

    def read(self):
        """
        Read a single line from the serial port. It is from the arduino.
        Returns:
            data (bytes): the read line from the arduino.
        """
        data = self.arduino.readline()
        if ( len(data) > 0 ):
            if ( data[0] != b'#'[0] ):
                print( data )
        return data

    def waitForArduinoStartTalk(self):
        """
        Wait until Arduino starts talking.    
        Returns:
            data (bytes): the read line from the arduino.
        """
        data = b''                                              # make an empty list
        while ( len(data) == 0 ):                               # wait for the device to start talking == download completed
            data = self.read()
        return data

    def waitForArduinoStopTalk(self):    
        """
        Wait until Arduino stops talking.    
        """
        data = b'0'                                             # make a non-empty list
        while ( len(data) > 0 ):                                # wait for the device to stop talking == help screen printed
            data = self.read()

if __name__ == "__main__":
    DataReader()