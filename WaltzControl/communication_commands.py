
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
        self.connected=True
        
    def check_connection(self):
        """Checks if Connection to serial port is open.
           Effecitvely only checks if you set serial.open() or serial.close()
           before. Not very useful as it is.
           
           Gives answer to self.connected.
           All modules can acces this variable.
        """
        if self.is_open:
            self.connected=True
        else:
            self.connected=False
            
    def check_connection_via_response(self,expected_response):
        """Checks if program gets a non zero response from serial port.
        
           This is useful since ser.is_open only accounts for this side of
           the serial port. So if Waltz Controler is shut off, serial.is_open
           will return True.
           We want to check for this case and respond as if whoel serial port
           was closed.
           Best used by checking it regularly, 
           e.g. with responses from get_coordinates.
           At the moment is it checked at get_coordinates which is executed
           every 0.5s via display get_coordinates.
        """
        #If you get no response (string with length 0)
        if not expected_response:
            print('No Response from serial port')
            #Set self.connected to False
            self.connected=False
            #And close serial connection from this side
            #super().close()
            #Can be opened via menu
        #If you get any nonzero response
        elif expected_response:
            #Connectio is open
            self.connected=True
            
    
  
    def get_response(self):
        """Reads from the serial connection and returns response as a string"""
        response = b''
        time.sleep(0.1)
        while self.in_waiting > 0:
            response += super().read(1)
        response=response.decode()
        return response
    
    def exit_program(self):
        """Closes the program"""
        super().close()
        print('Exiting program')
        exit()
        
    def close_connection(self):
        super().close()
        self.connected=False
    
    def open_connection(self):
        super().open()
        self.connected=True
        

