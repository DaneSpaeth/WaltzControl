import numpy as np
import math
lat=math.radians(49.3978620896919)

def equ_to_altaz(ha,dec):
    """ Transforms equatorial coordinates (hourangle, declination)
        to horizontal coordinates (azimuth,altitude).
        
        Input: ha in hours as float, dec in degree as float.
        
        Returns altitude and azimuth as float in degrees.
    """
    #Check if Input arrays have same dimensions
    if not np.isscalar(ha) and not np.isscalar(dec):
        if (len(ha)!=len(dec) or ha.ndim!=1 or dec.ndim!=1):
            return 0
    
    #Convert hour angle to radians
    #Convert hour angle to degree first and convert negative hour angles to
    #positive ones (e.g. -11 to 13)
    ha=ha+24*(ha<0)
    ha=np.radians(ha*15.)
    
    #Convert declination to radians
    dec=np.radians(dec)
    
    #Calculate altitude and azimuth (formulaes from celestial mechanics script
    #of Genevieve Parmentier)
    #For altitudwe have the formula:
    #sin(alt)=cos(ha)*cos(lat)*cos(dec)+sin(lat)*sin(dec))
    alt=np.arcsin(np.sin(lat)*np.sin(dec)+np.cos(lat)*np.cos(dec)*np.cos(ha))
    
    #For azimuth we have the formula
    #tan(az)=-sin(ha)/(cos(lat)*tan(dec)-sin(lat)*cos(ha))
    az=np.arctan2(np.sin(ha),(-np.cos(lat)*np.tan(dec)+np.sin(lat)*np.cos(ha)))
    
    #Convert alt and az to degrees
    alt=np.degrees(alt)
    az=np.degrees(az)
    
    #If Input was an array longer than 1 return the float arrays
    if not np.isscalar(alt):
        return (alt,az)
    
    #If Input was single values than also format the Output
    #In that case transform arrays to float
    alt=float(alt)
    az=float(az)
    formated_coord_list=[]
    #Also Format alt/az to +dd°mm'ss" as string
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

#print(equ_to_altaz(np.array([3,4]),np.array([30,40])))
print(equ_to_altaz(3,40))
#a=np.array([1.12345])
#print(type(a))
#print(np.isscalar(a))