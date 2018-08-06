import plot_coords
import matplotlib.pyplot as plt
from coord_operations import calc_alt_limit, calc_tree_limit, equ_to_altaz, altaz_to_equ, approx_obs_time

fig,ax1=plot_coords.plot_traj_limits_altaz_GUI(False,False,False,False)
#pos_plot.pop(0).remove()
#ax2.remove()
#plot_coords.add_star_and_traj(ax1,az,-3,30)

#plt.show()
current_ha=-3.5186111111
current_dec=25.0

plot_coords.add_current_pos(ax1,current_ha,current_dec)
plt.show()

