import time
import re
import threading
import pathlib
import math

from astropy.time import Time

import communication_commands as com
from hip_position_func import hip_position

class Lx200Commands(com.CommunicationCommands):
    """Inherits from CommunicationCommands and thus from Serial.
       Contains all commands, which use the lx200 protocol.
    """
    def __init__(self):
        super().__init__()
        self.LST=''
        self.LST_float=0
        
        #Store the current coordinates as strings
        self.ra=''
        self.dec=''
        self.ha=''
        #Store the current coordinates as floats (not always updated at the moment)
        self.ra_float=0
        self.dec_float=0
        self.ha_float=0
        
        #Store the Target coordinates as strings
        self.target_ra=False
        self.target_dec=False
        #Store only valid target_coordinates as list
        #0. Position meant to portray target_ra, 1. target_dec
        self.valid_target=[0,0]
        #Store the target coordinates as floats
        self.target_ra_float=False
        self.target_dec_float=False
        self.target_ha_float=False
        
        
    
    def get_coordinates(self):
        """ Gets Right ascension and Declination from the telescope controller and prints the values.
            We chose apropriate Output formats.
            
            Additionally checks if connection is open.
        """
        #Right Ascension
        inp=b'#:GR#'
        self.write(inp)
        unformated_ra=self.get_response()
        
        #Check connection with unformated_ra
        super().check_connection_via_response(unformated_ra)
        
        #Format hh mm.t
        if len(unformated_ra)==9:
            #Formating string output Right Ascension
            self.ra='{}h{}m{}s'.format(unformated_ra[0:2],
                                       unformated_ra[3:5],
                                       unformated_ra[6:8])
            #Formating float output Right Ascension
            self.ra_float=(int(unformated_ra[0:2])+
                           int(unformated_ra[3:5])/60.+
                           int(unformated_ra[6:8])/3600.)
            
        elif len(unformated_ra)==8:
            #Formating string output Declination
            self.ra='{}h{}m'.format(unformated_ra[0:2],
                                    unformated_ra[3:7])
            #Formating float output Right Ascension
            self.ra_float=(int(unformated_ra[0:2])+
                           float(unformated_ra[3:7])/60.)
        else:
            self.ra=unformated_ra
            self.ra_float=0
        
        #Declination
        inp=b'#:GD#'
        self.write(inp)
        unformated_dec=self.get_response()
        #Format dd mm ss
        if len(unformated_dec)==10:
            #Formating string output Declination
            self.dec='''{}°{}'{}"'''.format(unformated_dec[0:3],
                                            unformated_dec[4:6],
                                            unformated_dec[7:9])
            #Formating float output Declination
            #Case 1: Positive 
            if unformated_dec[0]=='+':
                self.dec_float=(int(unformated_dec[0:3])+
                                int(unformated_dec[4:6])/60.+
                                int(unformated_dec[7:9])/3600.)
            #Case 2: Negative
            elif unformated_dec[0]=='-':
                self.dec_float=(int(unformated_dec[0:3])-
                                int(unformated_dec[4:6])/60.-
                                int(unformated_dec[7:9])/3600.)
        #Format dd mm                                                           
        elif len(unformated_dec)==7:
            #Formating string output Declination
            self.dec="""{}°{}'""".format(unformated_dec[0:3],
                                         unformated_dec[4:6])
            #Formating float output Declination
            #Case 1: Positive 
            if unformated_dec[0]=='+':
                self.dec_float=(int(unformated_dec[0:3])+
                                int(unformated_dec[4:6])/60.)
            #Case 2: Negative
            elif unformated_dec[0]=='-':
                self.dec_float=(int(unformated_dec[0:3])-
                                int(unformated_dec[4:6])/60.)
        else:
            self.dec=unformated_dec
            self.dec_float=0
            
        #Check connection with unformated_dec
        super().check_connection_via_response(unformated_dec)
            
    def calculate_hour_angle(self):
        """ Takes self.ra and self.LST and calculates hour angle.
            Also calculates hour angle of target as float.
        """
        #Caution: It does not recalculate LST. So if you use it outside GUI it could lead to wrong results.
        #Make sure LST is refreshed.
        #If No Connection and therefore self.ra_float=0, close function
        if self.ra_float==0:
            return 0
        #Compute the hour angle in range [-12,12]
        self.ha_float=(self.LST_float-self.ra_float)
        self.target_ha_float=(self.LST_float-self.target_ra_float)
        #hour angles larger than 12 should be converted to negative numbers
        #e.g. 13 to -11
        if self.ha_float>12.:
            self.ha_float=self.ha_float-24.
        if self.target_ha_float>12.:
            self.target_ha_float=self.target_ha_float-24.
        #Get the sign of ha_float
        if self.ha_float>=0:
            sign='+'
        elif self.ha_float<0:
            sign='-'
        #Calculate the absolute of ha_float to convert it to hh mm ss
        ha_float=abs(self.ha_float)
        #Format hour angle to hh:mm:ss
        hours=int(ha_float)
        rest=abs(ha_float-hours)*60
        minutes=int(rest)
        rest=abs(rest-minutes)*60
        #We want to round seconds to get a more continous updating of seconds
        seconds=round(rest)
        #But we have to take care of rounding up to 60. Increase minutes by one in that case.
        if seconds==60:
            seconds=0
            minutes=minutes+1
        self.ha='{}{:02}h{:02}m{:02}s'.format(sign,hours,minutes,seconds)
        
        
    def start_move_west(self):
        """ Sends move west LX200 command to serial connection
        """
        inp=b'#:Mw#' 
        self.write(inp)
        
    def stop_move_west(self):
        """ Sends stop move west LX200 command to serial connection
        """
        inp=b'#:Qw#'
        self.write(inp)
    def start_move_north(self):
        inp=b'#:Mn#' 
        self.write(inp)
        
    def stop_move_north(self):
        inp=b'#:Qn#'
        self.write(inp)
        
    def start_move_south(self):
        inp=b'#:Ms#' 
        self.write(inp)
        
    def stop_move_south(self):
        inp=b'#:Qs#'
        self.write(inp)
        
    def start_move_east(self):
        inp=b'#:Me#' 
        self.write(inp)
        
    def stop_move_east(self):
        inp=b'#:Qe#'
        self.write(inp)
        
    def stop_all(self):
        """ Sends All Stop Commands to serial.
            
            Can't stop slew to target commands.
            Not used in the moment
        """
        self.stop_move_west()
        self.stop_move_east()
        self.stop_move_south()
        self.stop_move_north()
        
    def stop_at_current_pos(self):
        """Sets current coordinates as target coordinates and slews there.
        
           Used as STOP command.
           Normal Stop commands won't work during slew.
        """
        self.get_coordinates()
        self.set_target_ra_from_string(self.ra)
        self.set_target_dec_from_string(self.dec)
        self.slew_to_target()
    
    def move_west(self,duration=0.1):
        """Moves telescope in the west direction for a specified duration at the current slew rate.
       
           args: duration: duration of movement in seconds. Default value 0.1s.
           (This is just a dummy for the moment. 
           In the future we could for example hand the function the coordinate distance it should move.
           Moreover we could build a control panel like in Cartes du Ciel.)
        """
        #Start moving the telescope
        self.start_move_west()
        
        #Stoping the telescope movement
        #Wait specified duration until sending the STOP command
        time.sleep(duration)
        self.stop_move_west()
    
        #Now get and print the coordinates
        #Leave some time to respond
        time.sleep(0.1)
        self.get_coordinates()
    
    def move_east(self,duration=0.1):
        """Moves telescope in the east direction for a specified duration at the current slew rate.
       
           args: duration: duration of movement in seconds. Default value 0.1s.
           (This is just a dummy for the moment. 
           In the future we could for example hand the function the coordinate distance it should move.
           Moreover we could build a control panel like in Cartes du Ciel.)
        """
        #Start moving the telescope
        self.start_move_east()
        
        #Stoping the telescope movement
        #Wait specified duration until sending the STOP command
        time.sleep(duration)
        self.stop_move_east()
    
        #Now get and print the coordinates
        #Leave some time to respond
        time.sleep(0.1)
        self.get_coordinates()   
    
    def move_north(self,duration=0.1):
        """Moves telescope in the north direction for a specified duration at the current slew rate.
       
           args: duration: duration of movement in seconds. Default value 0.1s.
           (This is just a dummy for the moment. 
           In the future we could for example hand the function the coordinate distance it should move.
           Moreover we could build a control panel like in Cartes du Ciel.)
        """
        #Start moving the telescope
        self.start_move_north()
        
        #Stoping the telescope movement
        #Wait specified duration until sending the STOP command
        time.sleep(duration)
        self.stop_move_north()
    
        #Now get and print the coordinates
        #Leave some time to respond
        time.sleep(0.1)
        self.get_coordinates()
    
    def move_south(self,duration=0.1):
        """Moves telescope in the south direction for a specified duration at the current slew rate.
       
           args: duration: duration of movement in seconds. Default value 0.1s.
           (This is just a dummy for the moment. 
           In the future we could for example hand the function the coordinate distance it should move.
           Moreover we could build a control panel like in Cartes du Ciel.)
        """
        #Start moving the telescope
        self.start_move_south()
        
        #Stoping the telescope movement
        #Wait specified duration until sending the STOP command
        time.sleep(duration)
        self.stop_move_south()
    
        #Now get and print the coordinates
        #Leave some time to respond
        time.sleep(0.1)
        self.get_coordinates()
     
    def set_target_ra_from_string(self,ra):
        """ Takes string of RA in the format hh mm ss or hh mm.t and sets it as a target.
        """
        #Make sure input is a string
        ra=str(ra)
        #Check if ra is in the right form (account for high and low precision input)
        #Using Regluar Expression Package (re)
        match_obj=re.search( '\d{2}[h\s:]\d{2}[m\s:]\d{2}|\d{2}[h\s:]\d{2}\.\d',ra,re.I)
        if match_obj is None:
            self.target_ra=False
            print('Invalid Input! Use Format "hh mm ss" OR "hh mm.t"')
            return 0
        try:
            #We have two cases. Either hh mm ss or hh mm.t.
            #Format string correctly for the two cases.
            ra=match_obj.group()
            #Case 1 hh mm.t
            if ra[5]=='.':
                #Split up strings
                ra_h=ra[0:2]
                ra_m=ra[3:7]
                ra_s=''
                #Check if values are in right range
                if int(ra_h)>23 or float(ra_m)>=60:
                    print('Numbers too high. Hours not to exceed 23, minutes not to exceed 60')
                    self.target_ra=False
                    return 0
                else:
                    #Define input to serial, variable target_ra and target_ra_float
            
                    inp='#:Sr{}:{}#'.format(ra_h, ra_m)
                    self.target_ra='{} {}'.format(ra_h, ra_m)
                    self.target_ra_float=int(ra_h)+float(ra_m)/60.
            #Case 2 hh mm ss (also with units)
            elif ra[5]==' ' or ra[5]=='m' or ra[5]==':':
                #Split up strings
                ra_h=ra[0:2]
                ra_m=ra[3:5]
                ra_s=ra[6:8]
                #Check if values are in right range
                if int(ra_h)>23 or int(ra_m)>59 or int(ra_s)>59:
                    print('Numbers too high. Hours not to exceed 23, minutes and seconds not to exceed 60')
                    self.target_ra=False
                    return 0
                else:
                    #Define input to serial, variable target_ra and target_ra_float
                    inp='#:Sr{}:{}:{}#'.format(ra_h, ra_m, ra_s)
                    self.target_ra='{} {} {}'.format(ra_h, ra_m, ra_s)
                    self.target_ra_float=int(ra_h)+int(ra_m)/60.+int(ra_s)/3600.
            else:
                print('Invalid Input! Use Format "hh mm ss" OR "hh mm.t"')
                self.target_ra=False
                return 0
        except ValueError:
            print('Invalid Input! Use Format "hh mm ss" OR "hh mm.t"')
            self.target_ra=False
            return 0
        #Check if the input is observable and write input to serial port if yes
    
        ### An Dieser Stelle kontrollieren ob Koordinaten ok sind ###
        ### if Koordinaten ok ###
        
        inp=inp.encode()
        self.write(inp)
        #Set target_ra to valid_target
        self.valid_target[0]=self.target_ra
        
        #Receive 1 if input is valid and 0 if not
        #Convert to boolean
        #valid_input=self.get_response()
        valid_input='1'
        try:
            valid_input=bool(int(valid_input[0]))
        except ValueError:
            print('Received unexpected response!')
            return 0
        if valid_input:
            print('Target RA set to:',self.target_ra)
        else:
            print('Error: Target could not be set!')
            return 0
        
        #We supsect that outputs don't work properly.
        #So we for now just want to listen what serial port responds.
        output=self.get_response()
        print('Response from serial port:',output)
            
    def set_target_dec_from_string(self,dec):
        """ Takes string of DEC in the format [+/-]hh mm or [+/-]hh mm ss and sets it as a target.
        """
        #Make sure input is a string
        dec=str(dec)
        #Check if dec is in the right form (account for high and low precision input)
        #Using Regluar Expression Package (re)
        match_obj= re.match( '\s*[\+|\-]?\d{2}(.\d{2})+.?\s*\Z',dec)
        
        if match_obj is None:          
            print('Invalid Input! Use Format "[+/-]dd mm ss" OR "[+/-]dd mm"')
            return 0
        try:
            #We have two cases. Either dd mm or dd mm ss.
            #Format the string correctly for the two cases.
            #First strip of all whitespaces in front or behind string.
            dec=match_obj.group().strip()
            #Check if there is already a sign in front. 
            #If not: assume it to be positive and insert it as the frist character.
            if dec[0]!='+' and dec[0]!='-':
                dec='+'+dec
            #Case 1 dd mm
            if len(dec)<=7:
                #Split up strings
                dec_d=dec[0:3]
                dec_m=dec[4:6]
                dec_s=''
                #Check if values are in right range
                if int(dec_d)>90 or int(dec_d)<-90 or int(dec_m)>59:
                    print('Numbers too high. Degrees not to exceed 90, minutes not to exceed 59')
                    self.target_dec=False
                    return 0
                else:
                    ### An Dieser Stelle kontrollieren ob Koordinaten ok sind ###
                    ### if Koordinaten ok ###
                    
                    #Define input to serial, variable target_dec and target_dec_float
                    inp='#:Sd{}*{}#'.format(dec_d, dec_m)
                    self.target_dec="{} {}".format(dec_d, dec_m)
                    #Take care of right sign
                    if dec_d[0]=='+':
                        self.target_dec_float=(int(dec_d)+
                                               int(dec_m)/60.)
                    elif dec_d[0]=='-':
                        self.target_dec_float=(int(dec_d)-
                                               int(dec_m)/60.)
            #Case 2 dd mm ss
            elif len(dec)>7:
                #Split up strings
                dec_d=dec[0:3]
                dec_m=dec[4:6]
                dec_s=dec[7:9]
                #Check if values are in right range
                if int(dec_d)>90 or int(dec_d)<-90 or int(dec_m)>59 or int(dec_s)>59:
                    print('Numbers too high. Degrees not to exceed 90, minutes and seconds not to exceed 59')
                    self.target_dec=False
                    return 0
                else:
                    ### An Dieser Stelle kontrollieren ob Koordinaten ok sind ###
                    ### if Koordinaten ok ###
                    
                    #Define input to serial, variable target_dec and target_dec_float
                    inp='#:Sd{}*{}:{}#'.format(dec_d, dec_m, dec_s)
                    self.target_dec='''{} {} {}'''.format(dec_d, dec_m, dec_s)
                    #Take care of right sign
                    if dec_d[0]=='+':
                        self.target_dec_float=(int(dec_d)+
                                               int(dec_m)/60.+
                                               int(dec_s)/3600.)
                    elif dec_d[0]=='-':
                        self.target_dec_float=(int(dec_d)-
                                               int(dec_m)/60.-
                                               int(dec_s)/3600.)
        except ValueError:
            print('Invalid Input! Use Format "[+/-]dd mm ss" OR "[+/-]dd mm"')
            return 0
        #Check if the input is observable and write input to serial port if yes
        
        ### An Dieser Stelle kontrollieren ob Koordinaten ok sind ###
        ### if Koordinaten ok ###
        inp=inp.encode()
        self.write(inp)
        #Set target_dec to valid_target
        self.valid_target[1]=self.target_dec
        #Receive '1#' if input is valid and '0#' if not
        #Convert to boolean
        #valid_input=self.get_response()
        valid_input='1'
        try:
            valid_input=bool(int(valid_input[0]))
        except ValueError:
            print('Received unexpected response!')
            return 0
        if valid_input:
            print('Target DEC set to:',self.target_dec)
        else:
            print('Error: Target could not be set!')
            return 0
        
        #We supsect that outputs don't work properly.
        #So we for now just want to listen what serial port responds.
        output=self.get_response()
        print('Response from serial port:',output)
            
    def slew_to_target(self):
        """Slews to target.
           Target must be set before via set_target_dec_from_string and set_target_ra_from_string
        """
        coordinates_set=(self.target_ra, self.target_dec)
        if coordinates_set:
            inp=b'#:MS#'
            self.write(inp)
            out=self.get_response()
            #For the moment we want to just test which output we get
            #if out=='0':
                #print('Slewing to target')
            #else:
                #print('Error: Slewing not possible!')
            print("Response from serial port:",out)
            print('Test: Function: lx200commands.slew_to_target()')
        else:
            return 0
    
    def set_hip_target(self,hip_nr):   
        """ Takes a string hipparcos number an sets its coordinates as target coordinates.
            Uses hip_position from hip_position_func.py.
            At the moment it uses refraction corrected coordinates with standard values for 
            air temperature and air pressure.
        """ 
        try:
            hip_nr=int(hip_nr)
        except ValueError:
            print('Hipparcos Number must be integer')
            return 0
        if hip_nr>0 and hip_nr<118323:
            hip_nr=str(hip_nr)
        else:
            print('Invalid HIP number')
            #Set target_ra and target_dec to empty strings to make sure that we won't slew somewhere we dont expect
            self.target_ra=False
            self.target_dec=False
            return 0
        try:
            #We use the refraction uncorrected coordinates at the moment (We don't trust the correction too much)
            hip_coordinates=hip_position(hip_nr)
            ra=str(hip_coordinates[2])
            dec=str(hip_coordinates[3])
        except ValueError:
            print('Invalid HIP number')
            #Set target_ra and target_dec to empty strings to make sure that we won't slew somewhere we dont expect
            self.target_ra=False
            self.target_dec=False
            return 0
        
        #Set coordinates from hip_position as target_coordinates
        format_ra='{} {} {}'.format(ra[:2], ra[4:6],ra[8:10])
        format_dec='{} {} {}'.format(dec[:3], dec[7:9], dec[11:13])
        
        self.set_target_ra_from_string(format_ra)
        self.set_target_dec_from_string(format_dec)
        
    
    def toggle_precision(self):
        """Toggles between high and low precision setting.
        """
        inp=b'#:U#'
        self.write(inp)
        
    def set_speed_max(self):
        """ Sets Slew rate to max (fastest)
        """
        inp=b'#:RS#'
        self.write(inp)
        
    def set_speed_find(self):
        """ Sets Slew rate to Find Rate (second fastest)
        """
        inp=b'#:RM#'
        self.write(inp)
        
    def set_speed_center(self):
        """ Sets Slew rate to Centering Rate (second slowest)
        """
        inp=b'#:RC#'
        self.write(inp)
        
    def set_speed_guide(self):
        """ Sets Slew rate to Guiding Rate (slowest)
        """
        inp=b'#:RG#'
        self.write(inp)
        
    def sync_on_hip(self, hip_nr):
        """ Synchronizes telescope's coordinates with target coordinates.
            Target is set via Hipparcos identifier.
            Target needs to be aligned with the pinhole manually before.
            
            Could be wrong at this stage
        """
        #Assume you have aligned a Hipparcos star in the pinhole.
        #You know need to calculate the coordinates of the star again
        #(they could have changed in the time while you aligned it)
        #And set these coordinates as target (set_hip_target does that)
        #Then you need to synchronize to these coordinates since they should be
        #Perfectly in your pinhole in that moment.
        self.set_hip_target(hip_nr)
        inp=b'#:CM#'
        self.write(inp)
        
    def sync_on_coordinates(self):
        """ Synchronizes telescope's coordinates with target coordinates.
            Target coordinates are set via manual input. 
            Target needs to be aligned with the pinhole manually before.
            
            Could be wrong at this stage
        """
        if self.target_ra and self.target_dec:
            self.set_target_ra_from_string(self.target_ra)
            self.set_target_dec_from_string(self.target_dec)
            inp=b'#:CM#'
            self.write(inp)
            
    def get_LST(self):
        """ Calculates the current Local Sidereal Time.
            Also calculates LST as float in hours.
        """
        #Get current UTC from astropy.Time
        UTC_now=Time.now()
        #Convert to LST
        LST_now=UTC_now.sidereal_time('mean',longitude=8.724700212478638)
        #Get the format right. A bit unhandy here. Could be improved.
        LST_now=str(LST_now)
        (hours,h,rest)=LST_now.partition('h')
        #Add a zero to hours if single number
        hours=int(hours)
        (minutes,m,rest)=rest.partition('m')
        minutes=int(minutes)
        (seconds,s,rest)=rest.partition('s')
        #Round the seconds (format 12.545 to 13)
        #We want to round to get a more continous refreshing of the seconds
        seconds=round(float(seconds))
        #With rounding we could get 60 for seconds
        #In that case increse minutes by 1 and set seconds to 0
        if seconds ==60:
            seconds=0
            minutes=minutes+1
        LST_now='{:02}:{:02}:{:02}'.format(hours, minutes, seconds)
        #if String has changed update it
        if LST_now != self.LST:
            self.LST=LST_now
            
        #For different purposes also compute LST as a float in hours.
        self.LST_float=int(hours)+int(minutes)/60.+int(seconds)/3600.
            
    def slew_to_medium_position(self):
        """Defines a medium position, where it is always safe to slew to
           and moves there.
           
        """
        self.get_LST()
        #Set the medium position to Ra=LST (directly on meridian) and Dec=+30°
        medium_ra=self.LST
        medium_dec='+30 00 00'
        
        self.set_target_ra_from_string(medium_ra)
        self.set_target_dec_from_string(medium_dec)
        self.slew_to_target()
            
    #def check_set_medium_position(self):
        
        """ Checks for dangerous slewing commands,
            in which the telescope could slew through the hard limited area.
            
            Sets and slews to a intermediate step in medium position in this case.
            Afterwards sets 
        """
        #initial_target_ra=self.target_ra
        #initial_target_dec=self.target_dec
        #self.check_limits()
        #Current coordinates in up soft limit and target coordinates in low soft limit
        #if self.ra_up_soft_limit_reached and self.target_ra_low_soft_limit_reached:
            #self.slew_to_medium_position()
        #Current coordinates in low soft limit and target coordinates in up soft limit
        #elif self.ra_low_soft_limit_reached and self.target_ra_up_soft_limit_reached:
            #self.slew_to_medium_position()       
        #return(initial_target_ra, initial_target_dec)
            
    
    def slew_finished(self):
        """ Checks if slew has finished and was succesful.
            We choose 2 arcseconds as tolerance. (Higher might be better especially for RA)
        """
        #Calculate tolerance as decimal degree and hours
        tolerance_deg=2/3600
        tolerance_hours=2/(15*3600)
        if (abs(self.ra_float-self.target_ra_float)<tolerance_hours and
            abs(self.dec_float-self.target_dec_float)<tolerance_deg):
            return True
        else:
            return False
    
    def park_telescope(self):
        """Calculate park coordinates and slew there.
        
           Park in zenith position.
           Therefore calculate RA as LST, DEC as latitude.
        """
        #Calculate LST
        self.get_LST()
        #Set coordinates
        self.set_target_ra_from_string(self.LST)
        self.set_target_dec_from_string('+49 23 32')
        #Slew to target
        self.slew_to_target()
        
    def primary_mirror_pos(self):
        """Calculate position to insert primary mirror cover and slew there.
        """
        #Calculate LST
        self.get_LST()
        #Set coordinates 
        self.set_target_ra_from_string(self.LST)
        self.set_target_dec_from_string('+05 00 00')
        #Slew to target
        self.slew_to_target()
        
    def secondary_mirror_pos(self):
        """Calculate position to insert secondary mirror cover 
           and telescope cover and slew there.
        """
        #Calculate LST
        self.get_LST()
        #Set coordinates 
        self.set_target_ra_from_string(self.LST)
        self.set_target_dec_from_string('-25 00 00')
        #Slew to target
        self.slew_to_target()
        
        
        

        
        
        
        
            
            
