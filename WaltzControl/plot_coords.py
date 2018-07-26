import matplotlib.pyplot as plt
import numpy as np

from coord_operations import calc_alt_limit, calc_tree_limit, equ_to_altaz, altaz_to_equ

#Create az and alt_limit and tree_limit array
az=np.arange(-180,180,0.01)
alt_limit=np.zeros(len(az))
tree_limit=np.zeros(len(az))

#Calculate alt_limit for every az na tree_limit
for index in range(len(az)):
    alt_limit[index]=calc_alt_limit(az[index])
    tree_limit[index]=calc_tree_limit(az[index])

#Plot alt_limits vs az and tree limits  
plt.plot(az,alt_limit,color='red')
plt.plot(az,tree_limit,color='#00cc00',linewidth=0.0)
plt.fill_between(az,alt_limit,np.zeros(len(az)),color='red',alpha=1)
plt.fill_between(az,tree_limit,alt_limit,color='#00cc00',where=tree_limit>alt_limit,alpha=1)
plt.axis([-180, 180, 0, 90])
plt.xlabel('Azimuth[°]')
plt.ylabel('Altitude[°]')
plt.title('Waltz Pointing Limits')

#Define star (later function input)
star_az=-120
star_alt=35

#Calculate star ha and dec
star_ha,star_dec=altaz_to_equ(star_alt,star_az)
#Define star trajectory (dec stays constant, hour angle increases)
traj_ha=np.arange(star_ha,12,0.05)
traj_dec=np.ones(len(traj_ha))*star_dec
#Calculate star trajectory in alt and az
traj_alt=np.zeros(len(traj_ha))
traj_az=np.zeros(len(traj_ha))

for index in range(len(traj_ha)):
    traj_alt[index],traj_az[index],_,__=equ_to_altaz(traj_ha[index],traj_dec[index])
    

#plot star
plt.plot(star_az,star_alt,'b*')
plt.plot(traj_az,traj_alt,'b:')
plt.show()

#Define dec_limits and hour angle arrays
dec_limit=np.zeros(len(az))
ha=np.zeros(len(az))

#And tree limit array
dec_tree_limit=np.zeros(len(az))
ha_tree_limit=np.zeros(len(az))
dec_zero_alt=np.zeros(len(az))
#Transform altaz limits to ha,dec limits
for index in range(len(az)):
    ha[index],dec_limit[index]=altaz_to_equ(alt_limit[index],az[index])
    ha_tree_limit[index],dec_tree_limit[index]=altaz_to_equ(tree_limit[index],az[index])
    __,dec_zero_alt[index]=altaz_to_equ(0,az[index])
    
#Plot alt_limits vs az    
plt.plot(ha_tree_limit,dec_tree_limit,color='#00cc00',linewidth=0.0)
plt.plot(ha,dec_limit,color='red')
y_plot_limit=-30

plt.fill_between(ha_tree_limit,dec_tree_limit,np.ones(len(ha))*y_plot_limit,interpolate=True,color='#00cc00',where=dec_tree_limit>dec_limit,alpha=1)
plt.fill_between(ha,dec_limit,np.ones(len(ha))*y_plot_limit,color='red',alpha=1)
plt.axis([-12, 12, y_plot_limit, 90])
plt.xlabel('Hour Angle[h]')
plt.ylabel('Declination[°]')
plt.title('Waltz Pointing Limits')

#plot star
plt.plot(star_ha,star_dec,'b*')
plt.plot(traj_ha,traj_dec,'b:')
plt.show()  





