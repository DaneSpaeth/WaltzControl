from math import radians, degrees, sin, cos, tan, asin, atan2
import numpy as np

def equ_to_altaz(ha,dec):
    """ Transforms equatorial coordinates (hourangle, declination)
        to horizontal coordinates (azimuth,altitude).
        
        Input: ha in hours as float, dec in degree as float.
        
        Returns altitude and azimuth as float in degrees.
    """
    #Define Latitude in radians
    lat=radians(49.3978620896919)
    #Convert hour angle to radians
    #Convert hour angle to degree first and convert negative hour angles to
    #positive ones (e.g. -11 to 13)
    if ha < 0:
        ha=ha+24
    ha=radians(ha*15.)
    
    #Convert declination to radians
    dec=radians(dec)
    
    #Calculate altitude and azimuth (formulaes from celestial mechanics script
    #of Genevieve Parmentier)
    #For altitudewe have the formula:
    #sin(alt)=cos(ha)*cos(lat)*cos(dec)+sin(lat)*sin(dec))
    alt=asin(sin(lat)*sin(dec)+cos(lat)*cos(dec)*cos(ha))
    
    #For azimuth we have the formula
    #tan(az)=-sin(ha)/(cos(lat)*tan(dec)-sin(lat)*cos(ha))
    az=atan2(sin(ha),(-cos(lat)*tan(dec)+sin(lat)*cos(ha)))
    
    #Convert alt and az to degrees
    alt=degrees(alt)
    az=degrees(az)
    
    formated_coord_list=[]
    #Also Format alt/az to +dd°mm°ss as string
    #Get the sign of ha_float
    for coord in [alt,az]:
        if coord>=0:
            sign='+'
        elif coord<0:
            sign='-'
        #Calculate the absolute of coord to convert it to hh mm ss
        coord=abs(coord)
        #Format hour angle to hh:mm:ss
        deg=int(coord)
        rest=abs(coord-deg)*60
        minutes=int(rest)
        rest=abs(rest-minutes)*60
        #We want to round seconds to get a more continous updating of seconds
        seconds=round(rest)
        #But we have to take care of rounding up to 60. Increase minutes by one in that case.
        if seconds==60:
            seconds=0
            minutes=minutes+1
        coord='''{}{:02}°{:02}'{:02}"'''.format(sign,deg,minutes,seconds)
        formated_coord_list.append(coord)
        
    #Return altitude and azimuth
    return (alt,az,formated_coord_list[0],formated_coord_list[1])

def check_target_coordinates(alt,az):
        """Checks if target coordinates are observable and safe to slew.
        """
        #Check if target alt and az are set as floats
        if not alt or not az:
            return False
        
        #Define horizontal limit
        horizon_limit=12
        if alt>horizon_limit:
            return True
        else:
            return False

