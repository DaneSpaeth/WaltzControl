from math import radians, degrees, sin, cos, asin

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
    alt=asin(sin(lat)*sin(dec)+cos(lat)*cos(dec)*cos(ha))
    az=asin(cos(dec)*sin(ha)/cos(alt))
    
    #Convert alt and az to degrees
    alt=degrees(alt)
    az=degrees(az)
    #Return altitude and azimuth
    return (alt,az)
    
