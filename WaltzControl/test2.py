import plot_coords
import matplotlib.pyplot as plt

fig,star_plot, traj_plot, pos_plot, ax2=plot_coords.plot_traj_limits_altaz_GUI(-3,30,3,40)
#pos_plot.pop(0).remove()
ax2.remove()

plt.show()