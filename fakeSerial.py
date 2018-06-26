# fakeSerial.py
# D. Thiebaut
# Modified by Dane Späth
# A very crude simulator for PySerial assuming it
# is emulating an Arduino.
import time

# a Serial class emulator 
class Serial:

    # init(): the constructor.  Many of the arguments have default values
    # and can be skipped when calling the constructor.
    def __init__( self, port='COM1', baudrate = 19200, timeout=1,
                  bytesize = 8, parity = 'N', stopbits = 1, xonxoff=0,
                  rtscts = 0):
        self.name     = port
        self.port     = port
        self.timeout  = timeout
        self.parity   = parity
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.xonxoff  = xonxoff
        self.rtscts   = rtscts
        self._isOpen  = True
        self._receivedData = b''
        self._data = b''
        self.fake_ra=b"23:15:00#"
        self.fake_dec=b"+25:00:00#"
        self.fake_target_ra=b''
        self.fake_target_dec=b''
        self.in_waiting=len(self._data)
    # isOpen()
    # returns True if the port to the Arduino is open.  False otherwise
    def is_open( self ):
        return self._isOpen

    # open()
    # opens the port
    def open( self ):
        self._isOpen = True

    # close()
    # closes the port
    def close( self ):
        self._isOpen = False

    # write()
    # writes a string of characters to the Arduino
    def write( self, byte_input ):
        print( 'FakeSerial got: "' + byte_input.decode() + '"' )
        self._receivedData=b''
        self._receivedData += byte_input
        
        #Get Right Ascension
        if self._receivedData==b'#:GR#':
            self._data=self.fake_ra
            self.in_waiting=len(self._data)
            
        #Get Declination
        if self._receivedData==b'#:GD#':
            self._data=self.fake_dec
            self.in_waiting=len(self._data)
                                  
        #Set target_dec
        if self._receivedData[0:4] ==b'#:Sd':
            #format dd*mm
            if len(self._receivedData)==11:
                self.fake_target_dec=(self._receivedData[4:7]+b':'+
                                      self._receivedData[8:11])
            #format dd*mm:ss
            if len(self._receivedData)==14:
                self.fake_target_dec=(self._receivedData[4:7]+b':'+
                                      self._receivedData[8:10]+b':'+
                                      self._receivedData[11:14])
        #Set target_ra
        if self._receivedData[0:4] ==b'#:Sr':
            #Format hh:mm.t
            if len(self._receivedData)==12:
                self.fake_target_ra=self._receivedData[4:12]
            #Format hha:mm:ss
            if len(self._receivedData)==13:
                self.fake_target_ra=self._receivedData[4:13]
             
        if self._receivedData==b'#:MS#':
            print('Start Slewing')
            time.sleep(0.5)
            print('Stop Slewing')
            self.fake_ra=self.fake_target_ra
            self.fake_dec=self.fake_target_dec

    # read()
    # reads n characters from the fake Arduino. Actually n characters
    # are read from the string _data and returned to the caller.
    def read( self, n=1 ):
        s = self._data[0:n]
        self._data = self._data[n:]
        self.in_waiting=len(self._data)
        #print( "read: now self._data = ", self._data )
        return s     

    # readline()
    # reads characters from the fake Arduino until a \n is found.
    def readline( self ):
        returnIndex = self._data.index( "\n" )
        if returnIndex != -1:
            s = self._data[0:returnIndex+1]
            self._data = self._data[returnIndex+1:]
            self.in_waiting=len(self._data)
            return s
        else:
            return ""

    # __str__()
    # returns a string representation of the serial class
    def __str__( self ):
        return  "Serial<id=0xa81c10, open=%s>( port='%s', baudrate=%d," \
               % ( str(self.isOpen), self.port, self.baudrate ) \
               + " bytesize=%d, parity='%s', stopbits=%d, xonxoff=%d, rtscts=%d)"\
               % ( self.bytesize, self.parity, self.stopbits, self.xonxoff,
                   self.rtscts )