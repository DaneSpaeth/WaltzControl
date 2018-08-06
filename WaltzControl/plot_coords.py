import matplotlib.pyplot as plt
import numpy as np
import time

from coord_operations import calc_alt_limit, calc_tree_limit, equ_to_altaz, altaz_to_equ, approx_obs_time

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

def plot_traj_limits_altaz(star_ha,star_dec):
    """Plots limits and star trajectory in altitude and azimuth.
    """
    #Create az and alt_limit and tree_limit array
    az=np.arange(-180,180,0.01)
    alt_limit=np.zeros(len(az))
    tree_limit=np.zeros(len(az))

    #Calculate limits
    alt_limit=calc_alt_limit(az)
    tree_limit=calc_tree_limit(az)
    
    #Calculate star_az and star_alt
    star_alt,star_az,_,__=equ_to_altaz(star_ha,star_dec)
    #Define star trajectory (dec stays constant, hour angle increases)
    traj_ha=np.arange(-11.999,11.999,0.05)
    traj_dec=np.ones(len(traj_ha))*star_dec
    #Calculate star trajectory in alt and az
    traj_alt=np.zeros(len(traj_ha))
    traj_az=np.zeros(len(traj_ha))
    traj_alt,traj_az=equ_to_altaz(traj_ha,traj_dec)
    
    #Create array, where to put the hour angle ticks
    traj_ticks_ha=np.arange(np.round(star_ha),12)
    traj_ticks_dec=np.ones(len(traj_ticks_ha))*star_dec
    #Calculate the corresponding azimuth ticks
    __,traj_ticks_az=equ_to_altaz(traj_ticks_ha,traj_ticks_dec)
    #Tranform to integers for style
    traj_ticks_ha=traj_ticks_ha.astype(int)
    
    #Plot
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    #Add second axis to get x_labels at upper x-axis
    ax2 = ax1.twiny()
    
    #Plot alt_limit,tree_limits and star position and trajectory
    ax1.plot(az,alt_limit,color='red')
    ax1.plot(az,tree_limit,color='#00cc00',linewidth=0.0)
    ax1.plot(star_az,star_alt,'b*')
    ax1.plot(traj_az,traj_alt,'b.',markersize=0.75)
    #Fill the colors between the limits and 0 altitude
    ax1.fill_between(az,alt_limit,np.zeros(len(az)),color='red',alpha=1)
    ax1.fill_between(az,tree_limit,alt_limit,color='#00cc00',
                     where=tree_limit>alt_limit,alpha=1)
    #Set the axis limits
    ax1.set_xlim(-180,180)
    ax1.set_ylim(0,90)
    ax1.set_xlabel("Azimuth[°]")
    
    #Later we could exclude circumpolar stars
    #Create upper x-axis ticks and labels
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_xticks(traj_ticks_az)
    ax2.set_xticklabels(traj_ticks_ha)
    ax2.set_xlabel("Hour angle [h]")
    #plt.title('Waltz Pointing Limits')
    plt.show()
    

def plot_traj_limits_altaz_GUI(star_ha,star_dec,current_ha,current_dec):
    """Plots limits and star trajectory in altitude and azimuth.
    """
    #Create az and alt_limit and tree_limit array
    az=np.arange(-180,180,0.01)
    alt_limit=np.zeros(len(az))
    tree_limit=np.zeros(len(az))

    #Calculate limits
    alt_limit=calc_alt_limit(az)
    tree_limit=calc_tree_limit(az)
        
    
    #Plot
    fig = plt.figure(figsize=(13,6))
    ax1 = fig.add_subplot(111)
    return_list=[fig,ax1]

    
    #Plot alt_limit,tree_limits and star position and trajectory
    ax1.plot(az,alt_limit,color='red')
    ax1.plot(az,tree_limit,color='#00cc00',linewidth=0.0)
    
    #Fill the colors between the limits and 0 altitude
    ax1.fill_between(az,alt_limit,np.zeros(len(az)),color='red',alpha=1)
    ax1.fill_between(az,tree_limit,alt_limit,color='#00cc00',
                     where=tree_limit>alt_limit,alpha=1)
    
    #Set the axis limits
    ax1.set_xlim(-180,180)
    ax1.set_ylim(0,90)
    ax1.set_xlabel("Azimuth[°]")
    ax1.set_ylabel("Altitude[°]")
    
    #Optional: Add star and trajectory
    if star_ha and star_dec:
        star_plot,traj_plot,ax2=add_star_and_traj(ax1,star_ha,star_dec)
        return_list.append(star_plot)
        return_list.append(traj_plot)
        return_list.append(ax2)
         
    #Optional: Add current position    
    if current_ha and current_dec:
        pos_plot=add_current_pos(ax1,current_ha,current_dec)
        return_list.append(pos_plot)
    
    #Later we could exclude circumpolar stars
    #Create upper x-axis ticks and labels
    return return_list

def add_star_and_traj(axis,star_ha,star_dec):
    """Adds star and trajectory to existing axis in exsiting plot.
    """
    #Calculate star_az and star_alt
    star_alt,star_az,_,__=equ_to_altaz(star_ha,star_dec)
    #Define star trajectory (dec stays constant, hour angle increases)
    traj_ha=np.arange(-11.999,11.999,0.05)
    traj_dec=np.ones(len(traj_ha))*star_dec
    #Calculate star trajectory in alt and az
    traj_alt=np.zeros(len(traj_ha))
    traj_az=np.zeros(len(traj_ha))
    traj_alt,traj_az=equ_to_altaz(traj_ha,traj_dec)
    
    #Create array, where to put the hour angle ticks
    traj_ticks_ha=np.arange(np.round(star_ha),12)
    traj_ticks_dec=np.ones(len(traj_ticks_ha))*star_dec
    #Calculate the corresponding azimuth ticks
    __,traj_ticks_az=equ_to_altaz(traj_ticks_ha,traj_ticks_dec)
    #Tranform to integers for style
    traj_ticks_ha=traj_ticks_ha.astype(int)
    
    star_plot=axis.plot(star_az,star_alt,'b*')
    traj_plot=axis.plot(traj_az,traj_alt,'b.',markersize=0.75)
    #return_list.append(star_plot)
    #return_list.append(traj_plot)
    
    #Create upper x-axis ticks and labels
    #Add second axis to get x_labels at upper x-axis
    ax2 = axis.twiny()
    ax2.set_xlim(axis.get_xlim())
    ax2.set_xticks(traj_ticks_az)
    ax2.set_xticklabels(traj_ticks_ha)
    ax2.set_xlabel("Hour angle [h]")
    return star_plot,traj_plot,ax2

def add_current_pos(axis,current_ha,current_dec):
    """Adds current position to existing axis in existing plot.
    """
    current_alt,current_az,_,__=equ_to_altaz(current_ha,current_dec)
    pos_plot=axis.plot(current_az,current_alt,color='black',marker='o')
    return pos_plot
    
    

    





