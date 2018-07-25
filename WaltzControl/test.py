import numpy as np


board_lim=np.array([[12.0, 97.0],
                   [18.047683650516614, 101.22273624588037],
                   [19.922540694112776, 108.09973819537765],
                   [19.92473999691732, 112.96653118269231],
                   [18.1891109125214, 115.94832778139686],
                   [17.26156820756814, 119.6115621873876],
                   [17.3079984461787, 124.02768286442313],
                   [17.61337050520085, 128.47376745531645],
                   [16.514643086444128, 131.5063030183839],
                   [17.105176559235456, 135.7850030762675],
                   [15.574353529644203, 138.2131928476609],
                   [15.367408374687445, 141.5357258928432],
                   [13.465127305224598, 143.60311637027976],
                   [12.635376162837199,146.34084417895636],
                   [12.0, 150.0]])

#We want to find the two defined limits nearest to given az
#Then we want to take the highest limit of the two

#Compute difference between limit azs an given az
diff=board_lim[:,1]-az
#Take only positive and negative differences
pos=diff[diff>=0]
neg=diff[diff<0]
#Find one limit at lowest positive value of difference in az
up_az_lim=board_lim[np.where(diff==np.amin(pos))][0]
#The other at greatest negative value
low_az_lim=board_lim[np.where(diff==np.amax(neg))][0]

#Take only altitude entries
up_alt_lim=up_az_lim[0]
low_alt_lim=low_az_lim[0]

#Get Maximum of the two altitude limits
alt_limit=max(up_alt_lim,low_alt_lim)




#print(board_lim[1])