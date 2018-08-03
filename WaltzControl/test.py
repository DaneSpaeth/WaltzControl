from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np

from coord_operations import calc_alt_limit, calc_tree_limit, equ_to_altaz, altaz_to_equ, approx_obs_time

star_ha=3
star_dec=30

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
fig = Figure(figsize = (9, 6), facecolor = "white")
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
    
    
root = tk.Tk()
master = root
plot_frame=tk.Frame(root)
plot_frame.grid(row=0,column=0)
canvas = FigureCanvasTkAgg(fig, master = plot_frame)
canvas._tkcanvas.grid(row=0,column=0)

root.mainloop()
