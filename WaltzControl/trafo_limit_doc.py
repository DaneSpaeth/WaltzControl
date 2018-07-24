""" Takes Pointing Limits Document with ha,dec and limit mode.
    Returns Document with alt, az and limit mode.
"""
import numpy as np
import pathlib

from coord_operations import equ_to_altaz
ha_sign=[]
ha_hour=[]
ha_min=[]
dec_sign=[]
dec_deg=[]
dec_min=[]
mode=[]

#Define path to read_file 
current_path=pathlib.Path.cwd()
parrent_path=current_path.parent
file_path=parrent_path / 'pointing_limits' / 'pointing_limits_ha_dec.txt'
#With automatically closes the file in the end
with open(str(file_path), 'r') as readfile:
    #read first header line
    header=readfile.readline()
    
    #read line by line
    for line in readfile:
        #Strip off unused characters
        line=line.strip()
        #Split line in colums
        columns=line.split()
        
        ha_sign.append(columns[0][0])
        ha_hour.append(int(columns[0][1:]))
        ha_min.append(int(columns[1]))
        dec_sign.append(columns[2][0])
        dec_deg.append(int(columns[2][1:]))
        dec_min.append(int(columns[3]))
        mode.append(columns[4])

#Create arrays
ha_sign=np.array(ha_sign)       
ha_hour=np.array(ha_hour)
ha_min=np.array(ha_min)
dec_sign=np.array(dec_sign)
dec_deg=np.array(dec_deg)
dec_min=np.array(dec_min)
mode=np.array(mode)

#Calculate ha and dec as floats
ha=(ha_hour+ha_min/60)*(1*(ha_sign=='+')-1*(ha_sign=='-'))
dec=(dec_deg+dec_min/60)*(1*(dec_sign=='+')-1*(dec_sign=='-'))

#Create initial altitude and azimuth arrays
alt=np.zeros(len(ha))
az=np.zeros(len(ha))

#Define path to write file
file_path=parrent_path / 'pointing_limits' / 'pointing_limits_alt_az.txt'

#Transform coordinates
for index in range(len(ha)):
    (alt[index],az[index],dummy1,dummy2)=equ_to_altaz(ha[index],dec[index])
    line="{}    {}    {}\n".format(alt[index],az[index],mode[index])
    #With automatically closes the file in the end
    with open(str(file_path), 'a') as writefile:
        writefile.write(line)
    

