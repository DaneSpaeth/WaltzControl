import numpy as np

import hipparcos
from skyfield.api import utc
from skyfield.api import Star, load
from skyfield.api import Topos

def hip_position(hip_nr,temperature=15, pressure=1005):
    """ Returns uncorrected and refraction corrected apparent positions of stars in the Hipparcos catalogue.
    
        Position is specified to Waltz observer.
    """
    #Load list of planets and specify to earth to get obersver, then specify to location of Waltz
    planets=load('de421.bsp')
    earth=planets['earth']
    waltz=earth+Topos('49.3978620896919 N','8.724700212478638 E', elevation_m=562.0 )
    
    #Load current time.
    ts=load.timescale()
    t=ts.now()
    #t=t.utc #Convert

    #Load star catalogue coordinates from hipparcos.py module
    star=hipparcos.get(hip_nr)
    
    #Compute astrometric and apparent coordinates for Waltz at time t 
    astrometric= waltz.at(t).observe(star)
    apparent= astrometric.apparent()
    #Change to alt, az coordinates to compute refraction correction, then change back again
    #Change Temp and pressure
    alt, az, distancealt= apparent.altaz(temperature_C=temperature, pressure_mbar=pressure)
    corrected=apparent.from_altaz(alt=alt, az=az)
    
    #RA,DEC,Dist of refraction corrected positions
    ra_calc,dec_calc, distance=corrected.radec()
    
    
    #RA,DEC,Dist of refraction uncorrected positions
    ra_calc_without_refraction,dec_calc_without_refraction,distance =apparent.radec(epoch='date')

    
    return [ra_calc,dec_calc,ra_calc_without_refraction,dec_calc_without_refraction]
