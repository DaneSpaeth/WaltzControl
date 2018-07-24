from math import radians, degrees, sin, cos, tan, asin, acos, atan2
import numpy as np

#Define Latitude in radians
lat=radians(49.3978620896919)

#Define hoirzontal limit in altitude in degree 
horizon_limit=12

def equ_to_altaz(ha,dec):
    """ Transforms equatorial coordinates (hourangle, declination)
        to horizontal coordinates (azimuth,altitude).
        
        Input: ha in hours as float, dec in degree as float.
        
        Returns altitude and azimuth as float in degrees.
    """
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

def check_coordinates(alt,az):
        """Checks if coordinates are observable and safe to slew.
        """
        #Check if alt and az are set as floats
        if not alt or not az:
            return False
        
        #Check if altitude is above or below horizontal limit
        if alt>horizon_limit:
            return True
        else:
            return False
        
def calc_obs_time(ha,dec):
    """Calculates timespan, one can still observe star until it reaches 
       horizon limit.
    """
    #First calculate altitude and azimuth
    alt,az=equ_to_altaz(ha,dec)[:2]
    print(alt)
    print(az)
        
    #Save current hour angle in hours
    ha_now=ha
    print(ha_now)
    #Convert hour angle to radians
    ha=radians(ha*15.)
    
    #Convert declination to radians
    dec=radians(dec)
    horizon_limit_rad=radians(horizon_limit)
    
    def calc_ha_set(ha,dec):
        """Calculates hour angle at which star reaches horizontal limit.
        """
        
        #Calculate ha_Set in radian
        try:
            ha_set=acos((sin(horizon_limit_rad)-sin(lat)*sin(dec))/
                        (cos(lat)*cos(dec)))
            #Calculate ha_set in hours
            ha_set=degrees(ha_set)/15.
            return ha_set
        except ValueError:
            return False
    #Check if coordinates are within limits
    if not check_coordinates(alt,az):
        message = "Currently unobservable"
        return message
    else:
        ha_set=calc_ha_set(ha,dec)
        if not ha_set:
            message="Circumpolar"
            return message
        else:
            #Calculate observing time (in sidereal hours)
            obs_time=ha_set-ha_now
            #Convert to solar time units
            return obs_time

        
        
    
print(calc_obs_time(0.5,52.5))
