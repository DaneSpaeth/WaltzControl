from math import radians, degrees, sin, cos, tan, asin, acos, atan2
import numpy as np

#Define Latitude in radians
lat=radians(49.3978620896919)

#Define hoirzontal limit in altitude in degree 
horizon_limit=12

def equ_to_altaz(ha,dec):
    """ Transforms equatorial coordinates (hourangle, declination)
        to horizontal coordinates (azimuth,altitude).
        
        Input: ha in hours as float, dec in degree as float.
        
        Returns altitude and azimuth as float in degrees.
    """
    #Check if Input arrays have same dimensions
    if not np.isscalar(ha) and not np.isscalar(dec):
        if (len(ha)!=len(dec) or ha.ndim!=1 or dec.ndim!=1):
            return 0
    
    #Convert hour angle to radians
    #Convert hour angle to degree first and convert negative hour angles to
    #positive ones (e.g. -11 to 13)
    ha=ha+24*(ha<0)
    ha=np.radians(ha*15.)
    
    #Convert declination to radians
    dec=np.radians(dec)
    
    #Calculate altitude and azimuth (formulaes from celestial mechanics script
    #of Genevieve Parmentier)
    #For altitudwe have the formula:
    #sin(alt)=cos(ha)*cos(lat)*cos(dec)+sin(lat)*sin(dec))
    alt=np.arcsin(np.sin(lat)*np.sin(dec)+np.cos(lat)*np.cos(dec)*np.cos(ha))
    
    #For azimuth we have the formula
    #tan(az)=-sin(ha)/(cos(lat)*tan(dec)-sin(lat)*cos(ha))
    az=np.arctan2(np.sin(ha),(-np.cos(lat)*np.tan(dec)+np.sin(lat)*np.cos(ha)))
    
    #Convert alt and az to degrees
    alt=np.degrees(alt)
    az=np.degrees(az)
    
    #If Input was an array longer than 1 return the float arrays
    if not np.isscalar(alt):
        return (alt,az)
    
    #If Input was single values than also format the Output
    #In that case transform arrays to float
    alt=float(alt)
    az=float(az)
    formated_coord_list=[]
    #Also Format alt/az to +dd°mm'ss" as string
    #Get the sign of ha_float
    for coord in [alt,az]:
        if coord>=0:
            sign='+'
        elif coord<0:
            sign='-'
        #Calculate the absolute of coord to convert it to hh mm ss
        coord=abs(coord)
        #Format hour angle to hh:mm:ss
        deg=int(coord)
        rest=abs(coord-deg)*60
        minutes=int(rest)
        rest=abs(rest-minutes)*60
        #We want to round seconds to get a more continous updating of seconds
        seconds=round(rest)
        #But we have to take care of rounding up to 60. Increase minutes by one in that case.
        if seconds==60:
            seconds=0
            minutes=minutes+1
        coord='''{}{:02}°{:02}'{:02}"'''.format(sign,deg,minutes,seconds)
        formated_coord_list.append(coord)
        
    #Return altitude and azimuth
    return (alt,az,formated_coord_list[0],formated_coord_list[1])

def altaz_to_equ(alt,az):
    """ Transforms horizontal coordinates (azimuth,altitude).
        to equatorial coordinates (hourangle, declination).
        
        Input: alt in degrees as float or array of floats, 
               az in degrees as float or array of floats.
        
        Returns ha as float in hours and dec as float in degrees.
    """
    #Convert alt and az to radians
    alt=np.radians(alt)
    az=np.radians(az)
    
    #Calculate hour angle and declination (formulaes from celestial mechanics script
    #of Genevieve Parmentier)
    #For hour angle we have the formula:
    #tan(ha)=(sin(az))/(cos(lat)*tan(alt)+cos(az)*sin(lat))
    ha=np.arctan2(np.sin(az),np.cos(lat)*np.tan(alt)+np.cos(az)*np.sin(lat))
    
    #For declination we have the formula:
    #sin(dec)=sin(lat)*sin(alt)-cos(lat)*cos(alt)*cos(az)
    dec=np.arcsin(np.sin(lat)*np.sin(alt)-np.cos(lat)*np.cos(alt)*np.cos(az))
    
    #Convert ha to hours
    ha=np.degrees(ha)/15.
    #Convert dec to degrees
    dec=np.degrees(dec)
    
    return (ha, dec)
    
    
    
    
def check_coordinates(alt,az):
        """Checks if coordinates are observable and safe to slew.
        
           Returns True if coordinates do not reach limits.
           Returns False if coordinates are in limits.
        """
        #Check if alt and az are set as floats
        if (not isinstance(alt, (int, float)) 
            or not isinstance(az, (int, float))):
            return False
        
        #Calculate altitude limit
        alt_limit=calc_alt_limit(az)
            
        #Check if altitude is above or below limit
        if alt>=alt_limit:
            return True
        else:
            return False
        
    
def calc_alt_limit(az):
    """ Calculates altitude limits.
    
        Returns Altitude limit in degrees.
        Input: Array of az as floats between -180 and 180
    """
    #Check Input: If int or float make array
    if isinstance(az,(float,int)):
        az=np.array([az])
    elif isinstance(az,list):
        az=np.array(az)
    
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
    
    return alt_lim
    
        
def calc_obs_time(ha,dec):
    """Calculates timespan, one can still observe star until it reaches 
       horizon limit.
       
       Better use approx_obs_time.
    """
    
    #First calculate altitude and azimuth
    alt,az=equ_to_altaz(ha,dec)[:2]
        
    #Save current hour angle in hours
    ha_now=ha
    #Convert hour angle to radians
    ha=radians(ha*15.)
    
    #Convert declination to radians
    dec=radians(dec)
    horizon_limit_rad=radians(horizon_limit)
    
    def calc_ha_set(ha,dec):
        """Calculates hour angle at which star reaches horizontal limit.
        """
        
        #Calculate ha_Set in radian
        try:
            ha_set=acos((sin(horizon_limit_rad)-sin(lat)*sin(dec))/
                        (cos(lat)*cos(dec)))
            #Calculate ha_set in hours
            ha_set=degrees(ha_set)/15.
            return ha_set
        except ValueError:
            return False
    
    #Check if coordinates are within limits
    if not check_coordinates(alt,az):
        message = "Currently unobservable"
        return message
    else:
        ha_set=calc_ha_set(ha,dec)
        if not ha_set:
            message="Circumpolar"
            return message
        else:
            #Calculate observing time (in sidereal hours)
            obs_time=ha_set-ha_now
            #Convert to solar time units (in seconds)
            obs_time=obs_time*0.9972695601852*3600
            return obs_time
        
def approx_obs_time(star_ha,star_dec):
    """Calculates an approximate observing time for a star.
       
       
       Input: Hour angle in hours as float. Declination in degrees as float.
       Output: Observable time in solar seconds.
       Uses hard limits of the Waltz Telescope
    """
    #First check if star is already under a limit
    star_alt,star_az,_,__=equ_to_altaz(star_ha,star_dec)
    if not check_coordinates(star_alt,star_az):
        return 0
    
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
    return obs_time
        
def calc_tree_limit(az):
    """Calculates tree limit in altitude for given azimuth.
       Returns alt_limit in degrees.
       Input: azimuth in degrees.
    """
    #Define Tree limits as np.array
    #I put zero alt limit, where horizontal or cupboard limit is reached,
    #because we do not care about tree limits below hard limits.
    #Does not include all cupboard or horizontal areas, because it is zero there anyway
    
    #Check Input: If int or float make array
    if isinstance(az,(float,int)):
        az=np.array([az])
    elif isinstance(az,list):
        az=np.array(az)
    
    tree_lim=np.array([[0.0,-180.01],
                       [0.0,-165.3455807696162],
                       [13.926531858678072,-161.22484660697867],
                       [17.195599636413682,-157.44910241374103],
                       [0.0,-145.0],
                       [0.0,-148.91114359009313],
                       [21.58816304165209,-149.10471551491722],
                       [12.182100707176437,-135.7205489225959],
                       [17.29251687747958,-132.16310694376807],
                       [17.358959391076436,-128.24795814317287],
                       [16.554208994852967,-123.34078740486738],
                       [13.011626593972498,-115.7274970740633],
                       [0.0,-110.73615475166689],
                       [0.0,-100.57064217069362],
                       [0.0,-88.89096473867299],
                       [12.767315026462386,-81.11510631225428],
                       [13.63658755486348,-71.9033237952604],
                       [13.730797953998692,-62.34671848645827],
                       [16.517753594055026,-54.995932340824126],
                       [15.385051933925672,-45.40736739783195],
                       [14.249827605471754,-36.515993587901434],
                       [17.244394510206345,-29.80225310600212],
                       [16.786645206804543,-25.728955461859304],
                       [19.385806016233353,-22.649468723617428],
                       [17.815069758506976,-18.39429645277085],
                       [13.917540178597369,-13.926187167552994],
                       [15.800229806019255,-7.090540182345275],
                       [14.402137910308108,0.0],
                       [14.206429726562314,6.944851122938447],
                       [13.917540178597369,13.926187167552998],
                       [14.39736773524922,21.242902795231192],
                       [18.693114258587876,26.36363462208435],
                       [19.88987006933479,30.822460198427866],
                       [17.742310373009012,38.16015634421578],
                       [15.23857922621577,45.32492015300472],
                       [19.331358903370177,52.23568016291085],
                       [19.875106943741056,57.28528304962664],
                       [25.903731403911603,66.86068454273801],
                       [27.92145790178483,73.94757655442089],
                       [25.482784869502435,82.40122417583163],
                       [24.75519103243617,87.06221750457497],
                       [21.78914070627903,89.41320012139184],
                       [0.0,97.0],
                       [0.0,101.22273624588037],
                       [0.0,108.09973819537765],
                       [0.0,112.96653118269231],
                       [0.0,115.94832778139686],
                       [21.796949268702594,124.046616191669],
                       [0.0,119.6115621873876],
                       [20.05071675877851,126.59684863727593],
                       [0.0,124.02768286442313],
                       [0.0,146.34084417895636],
                       [0.0,180.01]])
    
    #Create multidimensional arrays of same shape
    #Idea is to have all differences of one given az in one line
    #So we want a board_lim_matrix where in each line all azimuths of
    #the board limits are represented. So it has as many lines as given azs
    #and in each line all limit_az are repeated
    az_lim_matrix=np.array(np.tile(tree_lim[:,1],az.shape[0]))
    az_lim_matrix=az_lim_matrix.reshape(az.shape[0],tree_lim.shape[0])

    #The az_matrix is constructed so that in each line only one value of 
    #input az is written
    #It has as many columns as azimuth limits 
    az_matrix=np.array(np.repeat(az,tree_lim.shape[0]))
    az_matrix=az_matrix.reshape(az.shape[0],tree_lim.shape[0])

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
    az_lim=tree_lim[:,1]
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
    up_alt_lim=tree_lim[up_indices,0]

    #Analog for low_alt_lim
    low_pos = np.searchsorted(az_lim[az_lim_sorted], low_az_lim)
    low_indices = az_lim_sorted[low_pos]
    low_alt_lim=tree_lim[low_indices,0]

    #Take the maximum element wise. So we always want the largest limit
    #of the two limit borders.
    tree_lim=np.maximum(up_alt_lim,low_alt_lim)
    
    return tree_lim



    
       


