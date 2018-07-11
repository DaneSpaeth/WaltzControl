
import time

#On Office PC module serial is not available (and not needed)
#Check if serial is available and connect to fakeSerial if not
try:
    import serial
    print('Importing serial')
except ImportError:
    print('Importing fakeSerial')
    import fakeSerial as serial

class CommunicationCommands(serial.Serial):
    """ Inherits from Serial class and adds basic communication functions """
    def __init__(self):
        #Open serial connection
        super().__init__(port='/dev/ttyS0',baudrate = 9600,timeout = 1)
        #Variable to save connection state
        self.connected=False
        #Check connection
        self.check_connection()
        
    def check_connection(self):
        """Checks if Connection to serial port is open.
           Gives answer to self.connected.
           All modules can acces this variable.
        """
        if self.is_open:
            self.connected=True
        else:
            self.connected=False
    
  
    def get_response(self):
        """Reads from the serial connection and returns response as a string"""
        response = b''
        time.sleep(0.1)
        while self.in_waiting > 0:
            response += self.read(1)
        response=response.decode()
        return response
    
    def exit_program(self):
        """Closes the program"""
        self.close()
        print('Exiting program')
        exit()
        
    def close_connection(self):
        self.close()
    
    def open_connection(self):
        self.open()
        

