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
    #For altitudwe have the formula:
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

def altaz_to_equ(alt,az):
    """ Transforms horizontal coordinates (azimuth,altitude).
        to equatorial coordinates (hourangle, declination).
        
        Input: alt in degrees as float, az in degrees as float.
        
        Returns ha as float in hours and dec as float in degrees.
    """
    #Convert alt and az to radians
    alt=radians(alt)
    az=radians(az)
    
    #Calculate hour angle and declination (formulaes from celestial mechanics script
    #of Genevieve Parmentier)
    #For hour angle we have the formula:
    #tan(ha)=(sin(az))/(cos(lat)*tan(alt)+cos(az)*sin(lat))
    ha=atan2(sin(az),cos(lat)*tan(alt)+cos(az)*sin(lat))
    
    #For declination we have the formula:
    #sin(dec)=sin(lat)*sin(alt)-cos(lat)*cos(alt)*cos(az)
    dec=asin(sin(lat)*sin(alt)-cos(lat)*cos(alt)*cos(az))
    
    #Convert ha to hours
    ha=degrees(ha)/15.
    #Convert dec to degrees
    dec=degrees(dec)
    
    return (ha, dec)
    
    
    
    
def check_coordinates(alt,az):
        """Checks if coordinates are observable and safe to slew.
        
           Returns True if coordinates do not reach limits.
           Returns False if coordinates are in limits.
        """
        #Check if alt and az are set as floats
        if not alt or not az:
            return False
        
        #Calculate altitude limit
        alt_limit=calc_alt_limit(az)
            
        #Check if altitude is above or below horizontal limit
        if alt>=alt_limit:
            return True
        else:
            return False
        
    
def calc_alt_limit(az):
    """ Calculates altitude limits.
    
        Returns Altitude limit in degrees.
    """
    #Return horizon limit outside of cupboard region
    if not 97.0 < az < 150.0:
        alt_limit=horizon_limit
        return alt_limit
    
    #Cupboard Limits
    
    #Define cupboard limits as np array
    #First and last limits are artificial horizontal limits
    #Up to these values the cupboard limits will act
    #Range from az=97° to 150°
    board_lim=np.array([[12.0, 97.0],
                       [18.047683650516614, 101.22273624588037],
                       [19.922540694112776, 108.09973819537765],
                       [19.92473999691732, 112.96653118269231],
                       [18.1891109125214, 115.94832778139686],
                       [17.26156820756814, 119.6115621873876],
                       [17.3079984461787, 124.02768286442313],
                       [17.61337050520085, 128.47376745531645],
                       [16.514643086444128, 131.5063030183839],
                       [17.105176559235456, 135.7850030762675],
                       [15.574353529644203, 138.2131928476609],
                       [15.367408374687445, 141.5357258928432],
                       [13.465127305224598, 143.60311637027976],
                       [12.635376162837199,146.34084417895636],
                       [12.0, 150.0]])
    
    #We want to find the two defined limits nearest to given az
    #Then we want to take the highest limit of the two

    #Compute difference between limit azs an given az
    diff=board_lim[:,1]-az
    #Take only positive and negative differences
    pos=diff[diff>=0]
    neg=diff[diff<0]
    #Find one limit at lowest positive value of difference in az
    up_az_lim=board_lim[np.where(diff==np.amin(pos))][0]
    #The other at greatest negative value
    low_az_lim=board_lim[np.where(diff==np.amax(neg))][0]

    #Take only altitude entries
    up_alt_lim=up_az_lim[0]
    low_alt_lim=low_az_lim[0]

    #Get Maximum of the two altitude limits
    alt_limit=max(up_alt_lim,low_alt_lim)
    
    return alt_limit
    
        
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


