import numpy as np
import math

lat=math.radians(49.3978620896919)
horizon_limit=12

az=np.array([-180,-150,-100,-50,0,30,146.34084417895636,60,97,120,147,180])

#Define limits. All limits are included. 
#We go from -180.01 to 180.01 to make sure that 180.0 is properly
#included. Also include 360.01. Shouldn't be inserted normally,
#but since it still works we include it for bad inputs.
limits=np.array([[horizon_limit, -180.01],
                    [horizon_limit, 97.0],
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
                    [horizon_limit, 150.0],
                    [horizon_limit, 180.01],
                    [horizon_limit, 360.01]])

#Create multidimensional arrays of same shape
#Idea is to have all differences of one given az in one line
#So we want a board_lim_matrix where in each line all azimuths of
#the board limits are represented. So it has as many lines as given azs
#and in each line all limit_az are repeated
az_lim_matrix=np.array(np.tile(limits[:,1],az.shape[0]))
az_lim_matrix=az_lim_matrix.reshape(az.shape[0],limits.shape[0])

#The az_matrix is constructed so that in each line only one value of 
#input az is written
#It has as many columns as azimuth limits 
az_matrix=np.array(np.repeat(az,limits.shape[0]))
az_matrix=az_matrix.reshape(az.shape[0],limits.shape[0])

#Calculate difference matrix
diff=az_lim_matrix-az_matrix

#Calculate matrices with only positive and negative values respectively
pos=(diff>=0)*diff
neg=(diff<0)*diff

#insert +/- infinity for 0, to avoid finding maxima/minima there 
pos[pos==0]=np.inf
neg[neg==0]=-np.inf

#Find one limit at lowest positive value of difference in az
#The other at greatest negative value
up_az_lim=az_lim_matrix[np.where(diff==np.amin(pos,axis=1,keepdims=True))]
low_az_lim=az_lim_matrix[np.where(diff==np.amax(neg,axis=1,keepdims=True))]

#Define 1D array with az_limits from limits
az_lim=limits[:,1]
#Get indices of sorted array. Note that it normally should be sorted already.
#But it is useful if one would insert new limits in unsorted order.
#Note that array is not really sorted, so we do not lose indices.
#We only get the indices with which you could sort the array
az_lim_sorted = np.argsort(az_lim)

#Perform searchsort with sorted indices. Search for up_az_lim values
#in general az_limits
up_pos = np.searchsorted(az_lim[az_lim_sorted], up_az_lim)
#get the indices, where you found the up_az_limits
up_indices = az_lim_sorted[up_pos]
#And take the up_alt_lim at these indices
up_alt_lim=limits[up_indices,0]

#Analog for low_alt_lim
low_pos = np.searchsorted(az_lim[az_lim_sorted], low_az_lim)
low_indices = az_lim_sorted[low_pos]
low_alt_lim=limits[low_indices,0]

#Take the maximum element wise. So we always want the largest limit
#of the two limit borders.
alt_lim=np.maximum(up_alt_lim,low_alt_lim)

print(alt_lim)



