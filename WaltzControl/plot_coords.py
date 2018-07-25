import matplotlib.pyplot as plt
import numpy as np

from coord_operations import calc_alt_limit

az=np.arange(-180,180,0.05)
alt_limit=np.zeros(len(az))
for index in range(len(az)):
    alt_limit[index]=calc_alt_limit(az[index])
    
plt.plot(az,alt_limit,color='red')
plt.axis([-180, 180, 0, 90])
plt.xlabel('Azimuth[°]')
plt.ylabel('Altitude[°]')
plt.title('Waltz Pointing Limits')

star_az=50
star_alt=30

plt.plot(star_az,star_alt,'b*')
plt.show()


