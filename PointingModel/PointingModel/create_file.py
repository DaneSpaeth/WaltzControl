#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hipparcos
from skyfield.api import utc
from skyfield.api import Star, load
from skyfield.api import Topos
import numpy as np
from datetime import datetime
import pathlib
import sidereal
import math
import matplotlib.pyplot as plt
import csv

###Content of ReadingFile, otheriwese problems at importing at fit_pointing_term2

#Choose the file here
#Filename and path using pathlib module
#File is in parrent_directory/data/pointing_stars_joined.txt
current_path=pathlib.Path.cwd()
parrent_path=current_path.parent
file_path=parrent_path / 'data' / 'pointing_stars_18july2018.txt'

#Reading in the file
readfile=open(file_path,'r')

header=readfile.readline()

#Initiallay empty arrays to store the information in
HIPnr=np.array([])
RAhour=np.array([])
RAmin=np.array([])
RAsec=np.array([])
DECdeg=np.array([])
DECarcmin=np.array([])
DECarcsec=np.array([])
LSThour=np.array([])
LSTmin=np.array([])
LSTsec=np.array([])
StringDate=np.array([])


#Read in line by line
for line in readfile:
    #Put each column in each line into a array columns    
    line=line.strip()
    columns=np.array(line.split())
    
    #Throw out data sets, in which one or more columns are missing ('NaN')
    if np.any(columns=='NaN'):
        continue
    
    #Write data into the arrays
    HIPnr=np.append(HIPnr,str(int(columns[0])))
    RAhour=np.append(RAhour,float(columns[1]))
    RAmin=np.append(RAmin,float(columns[2]))
    RAsec=np.append(RAsec,float(columns[3]))
    DECdeg=np.append(DECdeg,float(columns[4]))
    DECarcmin=np.append(DECarcmin,float(columns[5]))
    DECarcsec=np.append(DECarcsec,float(columns[6]))
    LSThour=np.append(LSThour,float(columns[7]))
    LSTmin=np.append(LSTmin,float(columns[8]))
    LSTsec=np.append(LSTsec,float(columns[9]))
    StringDate=np.append(StringDate,columns[10])

readfile.close()

#Calculate RA and DEC in hours/degrees
ra_obs=(RAhour+RAmin/(60)+RAsec/(60*60))
dec_obs=np.zeros(len(DECdeg))

#We need this loop to find the values, where we have -0 at DECdeg, be cautious what happens at +0.,
#Not very elegant, need to find another solution
for index in range(len(DECdeg)):
    if DECdeg[index]==-0.:
        print('Be cautious at index',index)
        dec_obs[index]=-1.*(np.absolute(DECdeg[index])+
                            DECarcmin[index]/(60)+
                            DECarcsec[index]/(60*60))
    else:
        dec_obs[index]=np.sign(DECdeg[index])*(np.absolute(DECdeg[index])+
                                                DECarcmin[index]/(60)+
                                                DECarcsec[index]/(60*60))

Date=np.array([])
for index in range(len(StringDate)):
    Date=np.append(Date,datetime.strptime(StringDate[index],'%d.%m.%Y'))
  
LST_float=LSThour+LSTmin/60.+LSTsec/3600.

###End Content of Reading File

###Actual Content of check_pointing_new.py

#load list of planets and specify to earth to get obersver, then specify to location of Waltz
planets=load('de421.bsp')
earth=planets['earth']
waltz=earth+Topos('49.3978620896919 N','8.724700212478638 E', elevation_m=562.0 )


ts= load.timescale()
t=ts.now()


###Compute UTC times of observations###
#Longitude in radian
elong=8.724700212478638/360*2*math.pi

julian_dates=np.array([])
ra_calc=np.zeros(len(LST_float))
dec_calc=np.zeros(len(LST_float))
ra_calc_uncorr=np.zeros(len(LST_float))
dec_calc_uncorr=np.zeros(len(LST_float))


for index in range(len(LST_float)):
    #SiderealTime doesn't seem to work with numpy. We will need to loop over it and take floats of arrays
    LST=sidereal.SiderealTime(float(LST_float[index]))
    #We have to convert that into Greenwhich sidereal time to convert it into UTC
    GST=LST.gst(elong)
    UTC=GST.utc(Date[index])
    #Give UTC the timezoneinfo=utc, important for skyfield utc
    UTC = UTC.replace(tzinfo=utc)
    
    #create a skyfield utc time
    t=ts.utc(UTC)
    
    #Build array julian_dates with observing times as julian dates
    julian_dates=np.append(julian_dates,t)

    #Load star from hipparcos.py
    stars=hipparcos.get(HIPnr[index])
    print(index)
    
    #Compute astrometric and apparent coordinates for Waltz at time t 
    astrometric= waltz.at(t).observe(stars)
    apparent= astrometric.apparent()
    #Change to alt, az coordinates to compute refraction correction, then change back again
    #Change Temp and pressure
    alt, az, distancealt= apparent.altaz(temperature_C=15.0, pressure_mbar=1005.0)
    corrected=apparent.from_altaz(alt=alt, az=az)
    
    #RA,DEC,Dist of refraction corrected positions
    ra,dec, distance=corrected.radec()
    
    #ra_calc and dec_calc contain all the info needed for the pointing model
    ra_calc[index]=ra.hours
    dec_calc[index]=dec.degrees
    #RA,DEC,Dist of refraction uncorrected positions
    ra_uncorr,dec_uncorr,distance_uncorr =apparent.radec(epoch='date')
    ra_calc_uncorr[index]=ra_uncorr.hours
    dec_calc_uncorr[index]=dec_uncorr.degrees
    
#Compute hour angles, it should be in the interval [-12,12]
ha_obs=LST_float-ra_obs
ha_obs=ha_obs+24*(ha_obs<-12.)-24*(ha_obs>12.)
ha_calc=LST_float-ra_calc
ha_calc=ha_calc+24*(ha_calc<-12.)-24*(ha_calc>12.)

#hour angles for uncorrected coordinates
ha_calc_uncorr=LST_float-ra_calc_uncorr
ha_calc_uncorr=(ha_calc_uncorr+
                24*(ha_calc_uncorr<-12.)-
                24*(ha_calc_uncorr>12.))
        
#With Refraction Correction
#Store results in a file
writefilename=parrent_path / 'data' / 'pointing_stars_coordinates_18july2018.txt'
writefile=open(writefilename,'w')
writefile.truncate()
writefile.write('HIP'+'\t'+
                'ha_calc'+'\t'+
                'ha_obs'+'\t'+
                'dec_calc'+'\t'+
                'dec_obs'+'\t'+
                'Date'+'\t'+
                'LST'+'\n')
for index in range(len(HIPnr)):
    writefile.write(HIPnr[index]+'\t'+
                    str(ha_calc[index])+'\t'+
                    str(ha_obs[index])+'\t'+
                    str(dec_calc[index])+'\t'+
                    str(dec_obs[index])+'\t'+
                    str(Date[index])+'\t'+
                    str(LST_float[index])+'\n')
writefile.close()

#Without Refraction Correction
#Store results in a file
writefilename=(parrent_path / 
               'data' / 
               'pointing_stars_coordinates_without_refr_corr_18july2018.txt')
writefile=open(writefilename,'w')
writefile.truncate()
writefile.write('HIP'+'\t'+
                'ha_calc_uncorr'+'\t'+
                'ha_obs'+'\t'+
                'dec_calc_uncorr'+'\t'+
                'dec_obs'+'\t'+
                'Date'+'\t'+
                'LST'+'\n')
for index in range(len(HIPnr)):
    writefile.write(HIPnr[index]+'\t'+
                    str(ha_calc_uncorr[index])+'\t'+
                    str(ha_obs[index])+'\t'+
                    str(dec_calc_uncorr[index])+'\t'+
                    str(dec_obs[index])+'\t'+
                    str(Date[index])+'\t'+
                    str(LST_float[index])+'\n')
writefile.close()
