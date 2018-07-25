import matplotlib.pyplot as plt
import numpy as np

from coord_operations import calc_alt_limit, altaz_to_equ

#Create az and alt_limit array
az=np.arange(-180,180,0.05)
alt_limit=np.zeros(len(az))

#Calculate alt_limit for every az
for index in range(len(az)):
    alt_limit[index]=calc_alt_limit(az[index])

#Plot alt_limits vs az    
plt.plot(az,alt_limit,color='red')
plt.axis([-180, 180, 0, 90])
plt.xlabel('Azimuth[°]')
plt.ylabel('Altitude[°]')
plt.title('Waltz Pointing Limits')

#Define star (later function input)
star_az=50
star_alt=30

#plot star
plt.plot(star_az,star_alt,'b*')
plt.show()

#Define dec_limits and hour angle arrays
dec_limit=np.zeros(len(az))
ha=np.zeros(len(az))

#Transodrm altaz limits to ha,dec limits
for index in range(len(az)):
    ha[index],dec_limit[index]=altaz_to_equ(alt_limit[index],az[index])
    
#Plot alt_limits vs az    
plt.plot(ha,dec_limit,color='red')
plt.axis([-12, 12, -30, 90])
plt.xlabel('Hour Angle[h]')
plt.ylabel('Declination[°]')
plt.title('Waltz Pointing Limits')

#plot star
#plt.plot(star_az,star_alt,'b*')
plt.show()  





