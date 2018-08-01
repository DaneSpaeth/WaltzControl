import matplotlib.pyplot as plt
import numpy as np
import time

from coord_operations import calc_alt_limit, calc_tree_limit, equ_to_altaz, altaz_to_equ

def plot_traj_and_limits(star_ha,star_dec):
    #Create az and alt_limit and tree_limit array
    az=np.arange(-180,180,0.01)
    alt_limit=np.zeros(len(az))
    tree_limit=np.zeros(len(az))


    alt_limit=calc_alt_limit(az)
    tree_limit=calc_tree_limit(az)

    #Plot alt_limits vs az and tree limits  
    plt.plot(az,alt_limit,color='red')
    plt.plot(az,tree_limit,color='#00cc00',linewidth=0.0)
    plt.fill_between(az,alt_limit,np.zeros(len(az)),color='red',alpha=1)
    plt.fill_between(az,tree_limit,alt_limit,color='#00cc00',
                     where=tree_limit>alt_limit,alpha=1)
    plt.axis([-180, 180, 0, 90])
    plt.xlabel('Azimuth[°]')
    plt.ylabel('Altitude[°]')
    plt.title('Waltz Pointing Limits')

    #Calculate star_az and star_alt
    star_alt,star_az,_,__=equ_to_altaz(star_ha,star_dec)
    print(star_alt)
    print(star_az)
    #Define star trajectory (dec stays constant, hour angle increases)
    traj_ha=np.arange(-11.999,11.999,0.05)
    traj_dec=np.ones(len(traj_ha))*star_dec
    #Calculate star trajectory in alt and az
    traj_alt=np.zeros(len(traj_ha))
    traj_az=np.zeros(len(traj_ha))


    traj_alt,traj_az=equ_to_altaz(traj_ha,traj_dec)
    

    #plot star
    plt.plot(star_az,star_alt,'b*')
    plt.plot(traj_az,traj_alt,'b.',markersize=0.5)
    plt.show()

    #Define dec_limits and hour angle arrays
    dec_limit=np.zeros(len(az))
    ha=np.zeros(len(az))

    #And tree limit array
    dec_tree_limit=np.zeros(len(az))
    ha_tree_limit=np.zeros(len(az))
    #Transform altaz limits to ha,dec limits
    ha,dec_limit=altaz_to_equ(alt_limit,az)
    ha_tree_limit,dec_tree_limit=altaz_to_equ(tree_limit,az)
    
    #Plot dec_limits vs ha    
    plt.plot(ha_tree_limit,dec_tree_limit,color='#00cc00',linewidth=0.0)
    plt.plot(ha,dec_limit,color='red')
    y_plot_limit=-30

    plt.fill_between(ha_tree_limit,dec_tree_limit,np.ones(len(ha))*y_plot_limit,
                     interpolate=True,color='#00cc00',
                     where=dec_tree_limit>dec_limit,alpha=1)
    plt.fill_between(ha,dec_limit,np.ones(len(ha))*y_plot_limit,color='red',alpha=1)
    plt.axis([-12, 12, y_plot_limit, 90])
    plt.xlabel('Hour Angle[h]')
    plt.ylabel('Declination[°]')
    plt.title('Waltz Pointing Limits')

    #plot star
    plt.plot(star_ha,star_dec,'b*')
    plt.plot(traj_ha,traj_dec,'b.',markersize=0.5)
    plt.show()

    #Approximately calculate time until hard limit is reached
    #If Star is circumpolar obs_time is 24 hours
    if star_dec > np.amax(dec_limit):
        sid_obs_time=24.
        obs_time=24.
    else:
        #If not circumpolar
        #Calculate the absolute differences between those dec_limits 
        #that are at hour angles larger than the stars hour angle
        #(to prevent to get the intersection on the eastern side)
        #and the stars declination
        dec_diff=np.abs(dec_limit[ha>star_ha]-star_dec)
        #Also cut out the hour angle values on the eastern side in ha array
        #Needed to get same dimension
        #Otherwise argmin wouldn't work
        ha_later=ha[ha>star_ha]
        #Hour Anlge at setting (reaching red limit) is at the same index as the
        #minimum of dec_diff
        ha_set=ha_later[np.argmin(dec_diff)]
        #Calculate the sidereal time until the star sets
        sid_obs_time=ha_set-star_ha
        #Sidereal hours convert to solar hours (normal time)
        #via 1h_sid=0.9972695601852h_sol
        obs_time=sid_obs_time*0.9972695601852
    return obs_time

def approx_obs_time(star_ha,star_dec):
    """Calculates an approximate observing time for a star.
       
       
       Input: Hour angle in hours as float. Declination in degrees as float.
       Output: Observable time in solar seconds.
       Uses hard limits of the Waltz Telescope
    """
    tstart=time.clock()
    #Create az and alt_limit array
    az=np.arange(-180,180,0.01)
    alt_limit=np.zeros(len(az))
    
    #Define dec_limits and hour angle arrays
    dec_limit=np.zeros(len(az))
    ha=np.zeros(len(az))
    
    #Calculate alt_limit for every az 
    alt_limit=calc_alt_limit(az)

    #Transform altaz limits to ha,dec limits
    ha,dec_limit=altaz_to_equ(alt_limit,az)
    tend=time.clock()
    print(round(tend-tstart, 3))
        
    tstart=time.clock()
    #Define star trajectory (dec stays constant, hour angle increases)
    traj_ha=np.arange(-11.999,11.999,0.05)
    traj_dec=np.ones(len(traj_ha))*star_dec
    
    #Approximately calculate time until hard limit is reached
    #If Star is circumpolar obs_time is 24 hours
    if star_dec > np.amax(dec_limit):
        sid_obs_time=24.
        obs_time=24.
    else:
        #If not circumpolar
        #Calculate the absolute differences between those dec_limits 
        #that are at hour angles larger than the stars hour angle
        #(to prevent to get the intersection on the eastern side)
        #and the stars declination
        dec_diff=np.abs(dec_limit[ha>star_ha]-star_dec)
        #Also cut out the hour angle values on the eastern side in ha array
        #Needed to get same dimension
        #Otherwise argmin wouldn't work
        ha_later=ha[ha>star_ha]
        #Hour Anlge at setting (reaching red limit) is at the same index as the
        #minimum of dec_diff
        ha_set=ha_later[np.argmin(dec_diff)]
        #Calculate the sidereal time until the star sets
        sid_obs_time=ha_set-star_ha
        #Sidereal hours convert to solar hours (normal time)
        #via 1h_sid=0.9972695601852h_sol
        obs_time=sid_obs_time*0.9972695601852
    tend=time.clock()
    print(round(tend-tstart, 3))
    return obs_time

plot_traj_and_limits(-3,-15)





