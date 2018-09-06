import statistics as st
import numpy as np
np.set_printoptions(threshold=np.inf)
import math
import pathlib


def reading_in_data(refr_corr=True):
    """Reads in Pointing data from file.
    """
    #Reading in Data
    HIPnr=np.array([])
    ha_calc=np.array([])
    ha_obs=np.array([])
    dec_calc=np.array([])
    dec_obs=np.array([])
    Date=np.array([])
    LST=np.array([])
    #Choose the file here
    #On Desktop (Dropbox)
    current_path=pathlib.Path.cwd()
    parrent_path=current_path.parent
    
    if refr_corr:
        file_path=(parrent_path /
                   'data' /
                   'pointing_stars_coordinates_18july2018_13deg_95kPa_last_points_removed.txt')
    else:
        file_path=(parrent_path /
                   'data' /
                   'pointing_stars_coordinates_without_refr_corr_18july2018.txt')
            
    
    #Reading in the file
    readfile=open(str(file_path),'r')
    header=readfile.readline()
    
    #Read in line by line
    for line in readfile:
        #Put each column in each line into a array columns    
        line=line.strip()
        columns=np.array(line.split())
        
        #Throw out data sets, in which one ore more columns are missing ('NaN')
        if np.any(columns=='NaN'):
            continue
        
        #Write data into the arrays
        HIPnr=np.append(HIPnr,str(int(columns[0])))
        ha_calc=np.append(ha_calc,float(columns[1]))
        ha_obs=np.append(ha_obs,float(columns[2]))
        dec_calc=np.append(dec_calc,float(columns[3]))
        dec_obs=np.append(dec_obs,float(columns[4]))
        Date=np.append(Date,columns[5])
        LST=np.append(LST,float(columns[7]))
        
    readfile.close()
        
    #We want to throw out data points which are too far off
    #Not active right now
    boolarray_ha=np.abs(ha_calc-ha_obs)<0.08
    boolarray_dec=np.abs(dec_calc-dec_obs)<0.08*15
    boolarray=np.logical_and(boolarray_ha,boolarray_dec)
    
    print(str(np.sum(boolarray))+' from '+str(len(boolarray))+' remaining')
        
    HIPnr=HIPnr[boolarray]
    ha_calc=ha_calc[boolarray]
    ha_obs=ha_obs[boolarray]
    dec_calc=dec_calc[boolarray]
    dec_obs=dec_obs[boolarray]
    Date=Date[boolarray]
    LST=LST[boolarray]
    
    #Assuming errors -> 
    #uncertainty of observed coord in degrees 
    #(chose 5 arcsec \approx 2/100*FOV)
    uncertainty_obs=(5./3600.)*2 
   
    ha_obs_error=np.ones(len(ha_obs))*uncertainty_obs/15.
    dec_obs_error=np.ones(len(dec_obs))*uncertainty_obs
   
    
        
        
    return (HIPnr, ha_calc, ha_obs, ha_obs_error,
            dec_calc, dec_obs, dec_obs_error,
            Date, LST)

def apply_IH(ha_obs,ha_obs_error,ha_calc,Date,ObservationDate='all'):
    """Calculates IH correction.
       According to formula ha_diff=-IH
       
       Input: ha_obs, ha_obs_error:
              (Observed hour angles with errors)
              ha_calc:
              (Calculated hour angles)
              Date:
              (Array of observed dates)
              ObservationDate:
              (String of chosen ObservationDate or 'all')
         
       Output: ha_diff, ha_diff_error:
               (Initial hour angles differences with errors)
               ha_corr, ha_corr_error:
               (Index corrected hour angles with errors)
               ha_diff_corr, ha_diff_corr_error:
               (Index corrected hour angle differences with errors)
    """
    
    #Initial Differences between observed and calculated coordinates
    ha_diff = ha_obs - ha_calc
    ha_diff_error=ha_obs_error
    
    #ha_corr will hold the corrected hour angles in the end
    ha_corr=ha_calc
    ha_corr_error=np.zeros(len(ha_corr))
    
    
    #We have to fit it for every observation date individually
    ###Should work but not tested yet
    if ObservationDate != 'all':
        #Fitting IH if we have picked only one date of observation 
        #(not much to worry about in this case)
        val = -np.mean(ha_diff)
        #Error as error of the mean (standarddeviation/sqrt(N))
        val_error=np.std(ha_diff)/(math.sqrt(len(ha_diff)))
        
        #Calculating chi^2 (we have +val since we have the formula DeltaHA=-IH
        chi_2=np.sum(((ha_diff+val)/ha_diff_error)**2)
        #Calculating Degrees of freedom (we have one parameter (IH))
        #So deg_free=number of datapoints-1
        deg_free=len(ha_diff)-1
        #Calculating reduced chi^2
        chi_2_red=chi_2/deg_free
        
        #We have a Minus sign to maintain definition of IH 
        #but change correction in the right direction
        ha_corr = ha_calc-val 
        ha_corr_error=val_error
        #We assume that model has no errors
        print('IH[h] at',ObservationDate,'=',round(val,4), 
              '+-',round(val_error,4), ' with chi^2_red=',chi_2_red)
       
    else:
        for element in np.unique(Date): 
            #np.unique gives an array in which all observation date 
            #occurr only once
            #Fitting IH for every Date individually
            val = -np.mean(ha_diff[Date==element]) 
            #We calculate the Value of IH at each Date
            #Negative IH means that observed coordinates are greater 
            #than calculated coordinates
            val_error=(np.std(ha_diff[Date==element])/
                       (math.sqrt(len(ha_diff[Date==element]))))
            #Calculating the error as error of the mean
            
            #Calculating chi^2
            chi_2=np.sum(((ha_diff+val)/ha_diff_error)**2)
            #Calculating Degrees of freedom (we have one parameter (IH))
            #So deg_free=number of datapoints-1
            deg_free=len(ha_diff)-1
            #Calculating reduced chi^2
            chi_2_red=chi_2/deg_free
            
            ###ha_corr needs to be changed each index individually 
            #since we want to have just one corrected ha in the end
            #We correct ha at each date
            ha_corr = ha_corr-val*(Date==element) 
            ha_corr_error=val_error*(Date==element) 
            #We assume that model has no errors
            print('IH[h] at',element,'=',round(val,4),
                  '+-',round(val_error,4), ' with chi^2_red=',chi_2_red)
            
    #Calculate new corrected differences between observed coordinates and corrected calculated coordinates        
    ha_diff_corr = ha_obs - ha_corr
    
    ha_diff_corr_error=np.sqrt(np.square(ha_obs_error)+
                               np.square(ha_corr_error))
            
    return (ha_diff, ha_diff_error,
            ha_corr, ha_corr_error,  
            ha_diff_corr, ha_diff_corr_error)


def apply_ID(dec_obs,dec_obs_error,dec_calc,Date, ObservationDate='all'):
    """Calculates ID correction.
       According to formula dec_diff=-ID
       
       Input: dec_obs, dec_obs_error:
              (Observed declinations with errors)
              dec_calc:
              (Calculated declinations)
              Date:
              (Array of observed dates)
              ObservationDate:
              (String of chosen ObservationDate or 'all')
         
       Output: dec_diff, dec_diff_error:
               (Initial declination differences with errors)
               dec_corr, dec_corr_error:
               (Index corrected declinations with errors)
               dec_diff_corr, dec_diff_corr_error:
               (Index corrected declination differences with errors)
    """
    #Initial Differences between observed and calculated coordinates
    dec_diff = dec_obs - dec_calc
   
    #Propagating errors for the differences
    dec_diff_error=dec_obs_error
   
   
    #In these arrays we will store the corrected calculated values
    #We just need them to initially have the same values 
    #as the calculated coordinates
    dec_corr=dec_calc
    dec_corr_error=np.zeros(len(dec_corr))
      
    #Fitting ID
    #We have to fit it for every observation date individually
    ###Should work but not tested yet
    if ObservationDate != 'all':
        #Fitting ID if we have picked only one date of observation 
        #(not much to worry about in this case)
        ID = -st.mean(dec_diff)
        ID_error=np.std(dec_diff)/(math.sqrt(len(dec_diff)))
        
        #Calculating chi^2 (we have +val since we have the formula DeltaHA=-IH
        chi_2=np.sum(((dec_diff+ID)/dec_diff_error)**2)
        #Calculating Degrees of freedom (we have one parameter (IH))
        #So deg_free=number of datapoints-1
        deg_free=len(dec_diff)-1
        #Calculating reduced chi^2
        chi_2_red=chi_2/deg_free
        
        
        dec_corr = dec_calc-ID
        dec_corr_error=ID_error
        #We assume that model has no errors
        print('ID[°] at',ObservationDate,'=',
              round(ID,4),'+-',round(ID_error,4),
              ' with chi^2_red=',chi_2_red)
    else:
        for element in np.unique(Date):          
           #Fitting ID analogously to fitting IH: look there for documentation
            ID = -np.mean(dec_diff[Date==element])
            ID_error=(np.std(dec_diff[Date==element])/
                       (math.sqrt(len(dec_diff[Date==element]))))
            
            #Calculating chi^2 (we have +val since we have the formula DeltaHA=-IH
            chi_2=np.sum(((dec_diff+ID)/dec_diff_error)**2)
            #Calculating Degrees of freedom (we have one parameter (IH))
            #So deg_free=number of datapoints-1
            deg_free=len(dec_diff)-1
            #Calculating reduced chi^2
            chi_2_red=chi_2/deg_free
        
            dec_corr = dec_corr-ID*(Date==element)
            dec_corr_error=ID_error*(Date==element)
            #We assume that model has no errors
            print('ID[°] at',element,'=',round(ID,4),
                  '+-',round(ID_error,4),
                  ' with chi^2_red=',chi_2_red)
           
    #Calculate new corrected differences between observed coordinates and corrected calculated coordinates        
    dec_diff_corr = dec_obs - dec_corr
    
    dec_diff_corr_error=np.sqrt(np.square(dec_obs_error)+
                                np.square(dec_corr_error))
    
    return (dec_diff, dec_diff_error,
            dec_corr, dec_corr_error,  
            dec_diff_corr, dec_diff_corr_error)

def apply_CH(ha_corr_first, ha_corr_first_error,
             dec_corr_first, dec_corr_first_error,
             ha_diff_corr, ha_diff_corr_error):
    """Calculates CH correction.
       According to formula ha_diff=-CH*1/cos(dec)
       
       Input: ha_corr_first, ha_corr_first_error:
              (Index corrected calculated hour angles with errors)
              dec_corr_first, dec_corr_first_error:
              (Index corrected calculated declinations with errors)
              ha_diff_corr, ha_diff_corr_error:
              (Index corrected calculated hour angle differences with errors)
         
       Output: ha_corr, ha_corr_error:
               (NP corrected hour angles with errors)
               CH, CH_error
               (value of CH and error)
    """
    #CH in units of hours
    sxx = sum((1/(np.cos(np.radians(dec_corr_first))))**2*
              1/(ha_diff_corr_error)**2)
    sxy = sum(ha_diff_corr*(1/np.cos(np.radians(dec_corr_first)))*
              1/(ha_diff_corr_error)**2)
    
    #We have a minus sign because we have the formula HA_diff=-CH*(1/cos(dec))
    CH = -(sxy/sxx)
    
    #Calculating chi^2 (we have +CH 
    #since we have the formula HA_diff=-CH*(1/cos(dec))
    chi_2=np.sum(((ha_diff_corr+CH/np.cos(np.radians(dec_corr_first)))
                  /ha_diff_corr_error)**2)
    #Calculating Degrees of freedom (we have one parameter (CH))
    #So deg_free=number of datapoints-1
    deg_free=len(ha_diff_corr)-1
    #Calculating reduced chi^2
    chi_2_red=chi_2/deg_free
    
    
    #For calculating the error
    s=sum(1/(ha_diff_corr_error)**2)
    sx=sum((1/np.cos(np.radians(dec_corr_first)))/(ha_diff_corr_error)**2)
    Delta=s*sxx-sx**2
    
    CH_error=s/Delta
    
    #First calculate the error
    ha_corr_error=np.sqrt((ha_corr_first_error)**2+
                          (1/np.cos(np.radians(dec_corr_first))*CH_error)**2+
                          (CH/(np.cos(np.radians(dec_corr_first)))**2*
                           np.sin(np.radians(dec_corr_first))*
                           dec_corr_first_error/15.)**2)

    #Calculating the corrected coordinates
    ha_corr = ha_corr_first-CH/np.cos(np.radians(dec_corr_first))

                        
    print('CH[h]=',CH,'+-',CH_error,' with chi^2_red=',chi_2_red)
    
    return (ha_corr, ha_corr_error, CH, CH_error)

def apply_NP(ha_corr_first, ha_corr_first_error,
             dec_corr_first, dec_corr_first_error,
             ha_diff_corr, ha_diff_corr_error):
    """Calculates NP correction.
       According to formula ha_diff=-NP*tan(dec)
       
       Input: ha_corr_first, ha_corr_first_error:
              (Index corrected calculated hour angles with errors)
              dec_corr_first, dec_corr_first_error:
              (Index corrected calculated declinations with errors)
              ha_diff_corr, ha_diff_corr_error:
              (Index corrected calculated hour angle differences with errors)
         
       Output: ha_corr, ha_corr_error:
               (NP corrected hour angles with errors)
               CH, CH_error
               (value of CH and error)
    """
              
                                  
    
    
    sxx = sum(np.tan(np.radians(dec_corr_first))**2*
              1/(ha_diff_corr_error)**2)
    sxy = sum(ha_diff_corr*np.tan(np.radians(dec_corr_first))*
              1/(ha_diff_corr_error)**2)
    
    #Need a minus sign
    NP = - (sxy/sxx)
    
    #Calculating chi^2 (we have +NP 
    #since we have the formula HA_diff=-NP*tan(dec))
    chi_2=np.sum(((ha_diff_corr+NP*np.tan(np.radians(dec_corr_first)))
                  /ha_diff_corr_error)**2)
    #Calculating Degrees of freedom (we have one parameter (NP))
    #So deg_free=number of datapoints-1
    deg_free=len(ha_diff_corr)-1
    #Calculating reduced chi^2
    chi_2_red=chi_2/deg_free
    
    
    #For calculating the error
    s=sum(1/(ha_diff_corr_error)**2)
    sx=sum((np.tan(np.radians(dec_corr_first)))/(ha_diff_corr_error)**2)
    Delta=s*sxx-sx**2
        
    NP_error=s/Delta
        
    #First calculate the error
    ha_corr_error=np.sqrt((ha_corr_first_error)**2+
                          (np.tan(np.radians(dec_corr_first))*NP_error)**2+
                          (NP/(np.cos(np.radians(dec_corr_first)))**2*
                           dec_corr_first_error/15.)**2)
    
    #Calculate corrected ha
    ha_corr = ha_corr_first-NP*np.tan(np.radians(dec_corr_first))
        
    print('NP[h]=',NP,'+-',NP_error,' with chi^2_red=',chi_2_red)
    
    return (ha_corr, ha_corr_error, NP, NP_error)

def apply_MA(ha_corr_first, ha_corr_first_error,
             dec_corr_first, dec_corr_first_error,
             ha_diff_corr, ha_diff_corr_error,
             dec_diff_corr, dec_diff_corr_error):
    """Calculates MA correction.
       According to formulas ha_diff=+MA*cos(ha)*tan(dec)
                             dec_diff=-MA*sin(ha)
       
       Input: ha_corr_first, ha_corr_first_error:
              (Index corrected calculated hour angles with errors)
              dec_corr_first, dec_corr_first_error:
              (Index corrected calculated declinations with errors)
              ha_diff_corr, ha_diff_corr_error:
              (Index corrected calculated hour angle differences with errors)
              dec_diff_corr, dec_diff_corr_error:
              (Index corrected calculated declination differences with errors)
         
       Output: ha_corr, ha_corr_error:
               (NP corrected hour angles with errors)
               dec_corr, dec_corr_error
               MA, MA_error
               (value of MA and error)
    """
    
    #We calculate MA and Me in degree. 
    #For that reason we introduce a factor of 15 
    #in all calculations with hour angles
    #It would look nicer 
    #if we would make this calculation just once in the beginning
        
    sxxh = sum((-np.cos(np.radians(ha_corr_first*15.))*
                np.tan(np.radians(dec_corr_first)))**2*
                1/(ha_diff_corr_error*15.)**2)
    sxyh = sum((ha_diff_corr*15)*
               (-np.cos(np.radians(ha_corr_first*15.))*
                np.tan(np.radians(dec_corr_first)))*
                1/(ha_diff_corr_error*15.)**2)

    sxxd = sum((np.sin(np.radians(15.*ha_corr_first)))**2*
                1/(dec_diff_corr_error)**2)
    sxyd = sum(dec_diff_corr*(np.sin(np.radians(15.*ha_corr_first)))*
               1/(dec_diff_corr_error)**2)
    
    #I believe that we have to set a minus sign here because we have the form
    #dec_diff=-MA*sin(ha) which should be present in Sxy
    MA = -(sxyh+sxyd)/(sxxh-sxxd)
    
    #Calculating chi^2 for ha and dec seperately
    chi_2_h=np.sum(((ha_diff_corr-
                     MA*np.cos(np.radians(ha_corr_first*15.))*
                     np.tan(np.radians(dec_corr_first)))
                     /ha_diff_corr_error)**2)
    chi_2_d=np.sum(((dec_diff_corr+
                    MA*np.sin(np.radians(ha_corr_first*15.)))
                    /dec_diff_corr_error)**2)
    #Now we can add these up
    chi_2=chi_2_h+chi_2_d
    #Calculating Degrees of freedom (we have one parameter (NP))
    #So deg_free=number of datapoints-1
    deg_free=len(ha_diff_corr)+len(dec_diff_corr)-1
    #Calculating reduced chi^2
    chi_2_red=chi_2/deg_free
        
    #For calculating the error
        
    sh=sum(1/(ha_diff_corr_error*15.)**2)
    sxh=sum(-np.cos(np.radians(ha_corr_first*15.))*
            np.tan(np.radians(dec_corr_first))/
            (ha_diff_corr_error*15.)**2)
        
    sd=sum(1/(dec_diff_corr_error)**2)
    sxd=sum(np.sin(np.radians(15.*ha_corr_first))/
            (dec_diff_corr_error)**2)
        
    s=sh+sd
    sx=sxh+sxd
    sxx=sxxh+sxxd
        
    Delta=s*sxx-sx**2
        
    MA_error=s/Delta
        
    #Calculate corrected HA and DEC and their errors
        
    ha_corr = (ha_corr_first+
               MA/15.*
               np.cos(np.radians(15.*ha_corr_first))*
               np.tan(np.radians(dec_corr_first)))
    dec_corr = dec_corr_first-MA*np.sin(np.radians(ha_corr_first*15.))
        
    ha_corr_error=np.sqrt(ha_corr_first_error**2+
                         (-np.cos(np.radians(ha_corr_first*15.))*
                          np.tan(np.radians(dec_corr_first))*
                          MA_error/15.)**2+
                         (MA/15.*
                          np.sin(np.radians(ha_corr_first*15.))*
                          np.tan(np.radians(dec_corr_first))*
                          ha_corr_first_error)**2+
                         (-MA/15.*
                          np.cos(np.radians(ha_corr_first*15.))*
                          1/(np.cos(np.radians(dec_corr_first)))**2*
                          dec_corr_first_error/15.)**2)
        
    dec_corr_error=np.sqrt((dec_corr_first_error)**2+
                           (np.sin(np.radians(ha_corr_first*15.))*
                            MA_error)**2+
                           (MA*np.cos(np.radians(ha_corr_first*15.))*
                            ha_corr_first_error*15.)**2)
        
    print('MA[°]=',MA,'+-',MA_error,' with chi^2_red=',chi_2_red)
    
    return(ha_corr, ha_corr_error,
           dec_corr, dec_corr_error,
           MA, MA_error)

def apply_ME(ha_corr_first, ha_corr_first_error,
             dec_corr_first, dec_corr_first_error,
             ha_diff_corr, ha_diff_corr_error,
             dec_diff_corr, dec_diff_corr_error):
    """Calculates ME correction.
       According to formulas ha_diff=-ME*sin(ha)*tan(dec)
                             dec_diff=-ME*cos(ha)
       
       Input: ha_corr_first, ha_corr_first_error:
              (Index corrected calculated hour angles with errors)
              dec_corr_first, dec_corr_first_error:
              (Index corrected calculated declinations with errors)
              ha_diff_corr, ha_diff_corr_error:
              (Index corrected calculated hour angle differences with errors)
              dec_diff_corr, dec_diff_corr_error:
              (Index corrected calculated declination differences with errors)
         
       Output: ha_corr, ha_corr_error:
               (NP corrected hour angles with errors)
               dec_corr, dec_corr_error
               MA, MA_error
               (Value of MA and error)
    """
    
    #We calculate  Me in degree. 
    #For that reason we introduce a factor of 15 
    #in all calculations with hour angles
    #It would look nicer 
    #if we would make this calculation just once in the beginning
        
    sxxh = sum((np.sin(np.radians(ha_corr_first*15.))*
                np.tan(np.radians(dec_corr_first)))**2*
                1/(ha_diff_corr_error*15.)**2)
    sxyh = sum((ha_diff_corr*15)*
               (np.sin(np.radians(ha_corr_first*15.))*
                np.tan(np.radians(dec_corr_first)))*
                1/(ha_diff_corr_error*15.)**2)
    
    sxxd = sum(np.cos(np.radians(ha_corr_first*15.))**2*
               1/(dec_diff_corr_error)**2)
    sxyd = sum(dec_diff_corr*np.cos(np.radians(ha_corr_first*15.))*
               1/(dec_diff_corr_error)**2)

    ME= -(sxyh+sxyd)/(sxxh+sxxd)
    
    #Calculating chi^2 for ha and dec seperately
    chi_2_h=np.sum(((ha_diff_corr+
                     ME*np.sin(np.radians(ha_corr_first*15.))*
                     np.tan(np.radians(dec_corr_first)))
                     /ha_diff_corr_error)**2)
    chi_2_d=np.sum(((dec_diff_corr+
                    ME*np.cos(np.radians(ha_corr_first*15.)))
                    /dec_diff_corr_error)**2)
    #Now we can add these up
    chi_2=chi_2_h+chi_2_d
    #Calculating Degrees of freedom (we have one parameter (NP))
    #So deg_free=number of datapoints-1
    deg_free=len(ha_diff_corr)+len(dec_diff_corr)-1
    #Calculating reduced chi^2
    chi_2_red=chi_2/deg_free
    
    #For calculating the error    
    sh=sum(1/(ha_diff_corr_error*15.)**2)
    sxh=sum(np.sin(np.radians(ha_corr_first*15.))*
            np.tan(np.radians(dec_corr_first))/
            (ha_diff_corr_error*15.)**2)
        
    sd=sum(1/(dec_diff_corr_error)**2)
    sxd=sum(np.cos(np.radians(15.*ha_corr_first))/(dec_diff_corr_error)**2)
        
    s=sh+sd
    sx=sxh+sxd
    sxx=sxxh+sxxd
        
    Delta=s*sxx-sx**2
        
    ME_error=s/Delta
               
    #Calculate corrected HA and DEC and their errors
        
    ha_corr = (ha_corr_first-
               ME/15*
               np.sin(np.radians(ha_corr_first*15.))*
               np.tan(np.radians(dec_corr_first)))
    dec_corr = dec_corr_first-ME*np.cos(np.radians(ha_corr_first*15.))
        
    ha_corr_error=np.sqrt(ha_corr_first_error**2+
                          (np.sin(np.radians(ha_corr_first*15.))*
                           np.tan(np.radians(dec_corr_first))*
                           ME_error/15.)**2+
                          (ME/15.*np.cos(np.radians(ha_corr_first*15.))*
                           np.tan(np.radians(dec_corr_first))*
                           ha_corr_first_error)**2+
                          (ME/15.*np.sin(np.radians(ha_corr_first*15.))*
                           1/(np.cos(np.radians(dec_corr_first)))**2*
                           dec_corr_first_error/15.)**2)
        
    dec_corr_error=np.sqrt((dec_corr_first_error)**2+
                           (np.cos(np.radians(ha_corr_first*15.))*
                            ME_error)**2+
                           (-ME*np.sin(np.radians(ha_corr_first*15.))*
                            ha_corr_first_error*15.)**2)
    dec_corr_error_ME=dec_corr_error
        
    
        
    print('ME[°]=',ME,'+-',ME_error,' with chi^2_red=',chi_2_red)
    
    return(ha_corr, ha_corr_error,
           dec_corr, dec_corr_error,
           ME, ME_error)

def apply_FO(ha_corr_first, ha_corr_first_error,
             dec_corr_first, dec_corr_first_error,
             dec_diff_corr, dec_diff_corr_error):
    """Calculates FO correction.
       According to formula dec_diff=-FO*cos(ha)
       
       Input: ha_corr_first, ha_corr_first_error:
              (Index corrected calculated hour angles with errors)
              dec_corr_first, dec_corr_first_error:
              (Index corrected calculated declinations with errors)
              dec_diff_corr, dec_diff_corr_error:
              (Index corrected calculated hour angle differences with errors)
         
       Output: dec_corr, dec_corr_error:
               (NP corrected hour angles with errors)
               FO, FO_error
               (value of FO and error)
    """
              
                                  
    
    
    sxx = sum(np.cos(np.radians(ha_corr_first*15.))**2*
              1/(dec_diff_corr_error)**2)
    sxy = sum(dec_diff_corr*np.cos(np.radians(ha_corr_first*15.))*
              1/(dec_diff_corr_error)**2)
    
    #Need a minus sign
    FO = - (sxy/sxx)
    
    #Calculating chi^2 (we have +FO 
    #since we have the formula dec_diff=-FO*cos(ha))
    chi_2=np.sum(((dec_diff_corr+FO*np.tan(np.radians(ha_corr_first*15.)))
                  /dec_diff_corr_error)**2)
    #Calculating Degrees of freedom (we have one parameter (FO))
    #So deg_free=number of datapoints-1
    deg_free=len(dec_diff_corr)-1
    #Calculating reduced chi^2
    chi_2_red=chi_2/deg_free
    
    
    #For calculating the error
    s=sum(1/(dec_diff_corr_error)**2)
    sx=sum((np.cos(np.radians(ha_corr_first*15.)))/(dec_diff_corr_error)**2)
    Delta=s*sxx-sx**2
        
    FO_error=s/Delta
        
    #First calculate the error
    dec_corr_error=np.sqrt((dec_corr_first_error)**2+
                          (np.cos(np.radians(ha_corr_first*15.))*FO_error)**2+
                          (FO*np.sin(np.radians(ha_corr_first*15.))*
                           ha_corr_first_error*15.)**2)
    
    #Calculate corrected ha
    dec_corr = dec_corr_first-FO*np.cos(np.radians(ha_corr_first*15.))
        
    print('FO[°]=',FO,'+-',FO_error,' with chi^2_red=',chi_2_red)
    
    return (dec_corr, dec_corr_error, FO, FO_error)

def apply_DCES(dec_corr_first, dec_corr_first_error,
               dec_diff_corr, dec_diff_corr_error):
    """Calculates DCES correction.
       According to formula dec_diff=-DCES*sin(dec)
       
       Input: dec_corr_first, dec_corr_first_error:
              (Index corrected calculated declinations with errors)
              ha_diff_corr, ha_diff_corr_error:
              (Index corrected calculated hour angle differences with errors)
         
       Output: dec_corr, dec_corr_error:
               (DCES corrected hour angles with errors)
               DCES, DCES_error
               (value of DCES and error)
    """
    sxx = sum(np.sin(np.radians(dec_corr_first))**2*
              1/(dec_diff_corr_error)**2)
    sxy = sum(dec_diff_corr*np.sin(np.radians(dec_corr_first))*
              1/(dec_diff_corr_error)**2)
    
    #Need a minus sign
    DCES = - (sxy/sxx)
    
    #Calculating chi^2 (we have +DCES 
    #since we have the formula dec_diff=-DCEs*sin(dec))
    chi_2=np.sum(((dec_diff_corr+DCES*np.sin(np.radians(dec_corr_first)))
                  /dec_diff_corr_error)**2)
    #Calculating Degrees of freedom (we have one parameter (DCES))
    #So deg_free=number of datapoints-1
    deg_free=len(dec_diff_corr)-1
    #Calculating reduced chi^2
    chi_2_red=chi_2/deg_free
    
    
    #For calculating the error
    s=sum(1/(dec_diff_corr_error)**2)
    sx=sum((np.sin(np.radians(dec_corr_first)))/(dec_diff_corr_error)**2)
    Delta=s*sxx-sx**2
        
    DCES_error=s/Delta
    
    #First calculate the error
    dec_corr_error=np.sqrt((dec_corr_first_error)**2+
                          (np.sin(np.radians(dec_corr_first))*DCES_error)**2+
                          (DCES*np.cos(np.radians(dec_corr_first))*
                           dec_corr_first_error)**2)
    
    #Calculate corrected ha
    dec_corr = dec_corr_first-DCES*np.sin(np.radians(dec_corr_first))
        
    print('DCES[°]=',DCES,'+-',DCES_error,' with chi^2_red=',chi_2_red)
    
    return (dec_corr, dec_corr_error, DCES, DCES_error)

def apply_DCEC(dec_corr_first, dec_corr_first_error,
               dec_diff_corr, dec_diff_corr_error):
    """Calculates DCEC correction.
       According to formula dec_diff=-DCEC*cos(dec)
       
       Input: dec_corr_first, dec_corr_first_error:
              (Index corrected calculated declinations with errors)
              ha_diff_corr, ha_diff_corr_error:
              (Index corrected calculated hour angle differences with errors)
         
       Output: dec_corr, dec_corr_error:
               (DCES corrected hour angles with errors)
               DCEC, DCEC_error
               (value of DCEC and error)
    """
    sxx = sum(np.cos(np.radians(dec_corr_first))**2*
              1/(dec_diff_corr_error)**2)
    sxy = sum(dec_diff_corr*np.cos(np.radians(dec_corr_first))*
              1/(dec_diff_corr_error)**2)
    
    #Need a minus sign
    DCEC = - (sxy/sxx)
    
    #Calculating chi^2 (we have +DCEC 
    #since we have the formula dec_diff=-DCEC*cos(dec))
    chi_2=np.sum(((dec_diff_corr+DCEC*np.cos(np.radians(dec_corr_first)))
                  /dec_diff_corr_error)**2)
    #Calculating Degrees of freedom (we have one parameter (DCEC))
    #So deg_free=number of datapoints-1
    deg_free=len(dec_diff_corr)-1
    #Calculating reduced chi^2
    chi_2_red=chi_2/deg_free
    
    
    #For calculating the error
    s=sum(1/(dec_diff_corr_error)**2)
    sx=sum((np.cos(np.radians(dec_corr_first)))/(dec_diff_corr_error)**2)
    Delta=s*sxx-sx**2
        
    DCEC_error=s/Delta
    
    #First calculate the error
    dec_corr_error=np.sqrt((dec_corr_first_error)**2+
                          (np.cos(np.radians(dec_corr_first))*DCEC_error)**2+
                          (DCEC*np.sin(np.radians(dec_corr_first))*
                           dec_corr_first_error)**2)
    
    #Calculate corrected ha
    dec_corr = dec_corr_first-DCEC*np.cos(np.radians(dec_corr_first))
        
    print('DCEC[°]=',DCEC,'+-',DCEC_error,' with chi^2_red=',chi_2_red)
    
    return (dec_corr, dec_corr_error, DCEC, DCEC_error)

def apply_DLIN(dec_corr_first, dec_corr_first_error,
               dec_diff_corr, dec_diff_corr_error):
    """Calculates linear correction.
       According to formula dec_diff=-DLIN*dec
       
       Input: dec_corr_first, dec_corr_first_error:
              (Index corrected calculated declinations with errors)
              ha_diff_corr, ha_diff_corr_error:
              (Index corrected calculated hour angle differences with errors)
         
       Output: dec_corr, dec_corr_error:
               (DLIN corrected hour angles with errors)
               DLIN, DLIN_error
               (value of DLIN and error)
    """
    sxx = sum(dec_corr_first**2*1/(dec_diff_corr_error)**2)
    sxy = sum(dec_diff_corr*dec_corr_first*1/(dec_diff_corr_error)**2)
    
    #Need a minus sign
    DLIN = - (sxy/sxx)
    
    #Calculating chi^2 (we have +DLIN 
    #since we have the formula dec_diff=-DLIN*dec)
    chi_2=np.sum(((dec_diff_corr+DLIN*dec_corr_first)
                  /dec_diff_corr_error)**2)
    #Calculating Degrees of freedom (we have one parameter (DLIN))
    #So deg_free=number of datapoints-1
    deg_free=len(dec_diff_corr)-1
    #Calculating reduced chi^2
    chi_2_red=chi_2/deg_free
    
    
    #For calculating the error
    s=sum(1/(dec_diff_corr_error)**2)
    sx=sum((dec_corr_first/dec_diff_corr_error)**2)
    Delta=s*sxx-sx**2
        
    DLIN_error=s/Delta
    
    
    #First calculate the error
    dec_corr_error=np.sqrt((dec_corr_first_error)**2+
                          (dec_corr_first*DLIN_error)**2+
                          (DLIN*
                           dec_corr_first_error)**2)
    
    #Calculate corrected ha
    dec_corr = dec_corr_first-DLIN*dec_corr_first
        
    print('DLIN=',DLIN,'+-',DLIN_error,' with chi^2_red=',chi_2_red)
    
    return (dec_corr, dec_corr_error, DLIN, DLIN_error)

def apply_TF(ha_corr_first, ha_corr_first_error,
             dec_corr_first, dec_corr_first_error,
             ha_diff_corr, ha_diff_corr_error,
             dec_diff_corr, dec_diff_corr_error):
    """Calculates TF correction.
       According to formulas ha_diff=-TF*cos(phi)*sin(ha)*1/cos(dec)
                             dec_diff=-TF*(cos(phi)*cos(ha)*sin(dec)
                                           -sin(phi)*cos(dec))
       
       Input: ha_corr_first, ha_corr_first_error:
              (Index corrected calculated hour angles with errors)
              dec_corr_first, dec_corr_first_error:
              (Index corrected calculated declinations with errors)
              ha_diff_corr, ha_diff_corr_error:
              (Index corrected calculated hour angle differences with errors)
              dec_diff_corr, dec_diff_corr_error:
              (Index corrected calculated declination differences with errors)
         
       Output: ha_corr, ha_corr_error:
               (NP corrected hour angles with errors)
               dec_corr, dec_corr_error
               TF, TF_error
               (Value of MA and error)
    """
    
    #We calculate  TF in degree. 
    #For that reason we introduce a factor of 15 
    #in all calculations with hour angles
    #It would look nicer 
    #if we would make this calculation just once in the beginning
    
    #Define site's latitude
    phi=49.3978620896919
    
    sxxh = sum((np.cos(np.radians(phi))*
                np.sin(np.radians(ha_corr_first*15.))*
                1/np.cos(np.radians(dec_corr_first)))**2*
                1/(ha_diff_corr_error*15.)**2)
    sxyh = sum(ha_diff_corr*15*
               np.cos(np.radians(phi))*
               np.sin(np.radians(ha_corr_first*15.))*
               1/np.cos(np.radians(dec_corr_first))*
               1/(ha_diff_corr_error*15.)**2)
    
    sxxd = sum((np.cos(np.radians(phi))*
               np.cos(np.radians(ha_corr_first*15.))*
               np.sin(np.radians(dec_corr_first))-
               np.sin(np.radians(phi))*
               np.cos(np.radians(dec_corr_first)))**2*
               1/(dec_diff_corr_error)**2)
    sxyd = sum(dec_diff_corr*
               (np.cos(np.radians(phi))*
               np.cos(np.radians(ha_corr_first*15.))*
               np.sin(np.radians(dec_corr_first))-
               np.sin(np.radians(phi))*
               np.cos(np.radians(dec_corr_first)))*
               1/(dec_diff_corr_error)**2)

    TF= -(sxyh+sxyd)/(sxxh+sxxd)
    
    #Calculating chi^2 for ha and dec seperately
    chi_2_h=np.sum((ha_diff_corr+
                     TF*(np.cos(np.radians(phi))*
                         np.sin(np.radians(ha_corr_first*15.))*
                         1/np.cos(np.radians(dec_corr_first)))
                     /ha_diff_corr_error)**2)
    chi_2_d=np.sum((dec_diff_corr+
                    TF*(np.cos(np.radians(phi))*
                        np.cos(np.radians(ha_corr_first*15.))*
                        np.sin(np.radians(dec_corr_first))-
                        np.sin(np.radians(phi))*
                        np.cos(np.radians(dec_corr_first)))
                    /dec_diff_corr_error)**2)
    #Now we can add these up
    chi_2=chi_2_h+chi_2_d
    #Calculating Degrees of freedom (we have one parameter (NP))
    #So deg_free=number of datapoints-1
    deg_free=len(ha_diff_corr)+len(dec_diff_corr)-1
    #Calculating reduced chi^2
    chi_2_red=chi_2/deg_free
    
    #For calculating the error    
    sh=sum(1/(ha_diff_corr_error*15.)**2)
    sxh=sum(np.cos(np.radians(phi))*
            np.sin(np.radians(ha_corr_first*15.))*
            1/np.cos(np.radians(dec_corr_first))/
            (ha_diff_corr_error*15.)**2)
        
    sd=sum(1/(dec_diff_corr_error)**2)
    sxd=sum((np.cos(np.radians(phi))*
             np.cos(np.radians(ha_corr_first*15.))*
             np.sin(np.radians(dec_corr_first))-
             np.sin(np.radians(phi))*
             np.cos(np.radians(dec_corr_first)))
             /(dec_diff_corr_error)**2)
        
    s=sh+sd
    sx=sxh+sxd
    sxx=sxxh+sxxd
        
    Delta=s*sxx-sx**2
        
    TF_error=s/Delta
               
    #Calculate corrected HA and DEC and their errors
        
    ha_corr = (ha_corr_first-
               TF/15.*
               np.cos(np.radians(phi))*
               np.sin(np.radians(ha_corr_first*15.))*
               1/np.cos(np.radians(dec_corr_first)))
    dec_corr = (dec_corr_first-
                TF*
                (np.cos(np.radians(phi))*
                 np.cos(np.radians(ha_corr_first*15.))*
                 np.sin(np.radians(dec_corr_first))-
                 np.sin(np.radians(phi))*
                 np.cos(np.radians(dec_corr_first))))
    
        
    ha_corr_error=np.sqrt(ha_corr_first_error**2+
                          (np.cos(np.radians(phi))*
                           np.sin(np.radians(ha_corr_first*15.))*
                           1/np.cos(np.radians(dec_corr_first))*
                           TF_error/15.)**2+
                          (TF/15.*np.cos(np.radians(phi))*
                           np.sin(np.radians(ha_corr_first*15.))*
                           1/np.cos(np.radians(dec_corr_first))*
                           ha_corr_first_error)**2+
                          (TF/15.*np.cos(np.radians(phi))*
                           np.cos(np.radians(ha_corr_first*15.))*
                           1/np.cos(np.radians(dec_corr_first))*
                           np.tan(np.radians(dec_corr_first))*
                           dec_corr_first_error/15.)**2)
                          
    term=(np.cos(np.radians(phi))*
          np.cos(np.radians(ha_corr_first*15.))*
          np.sin(np.radians(dec_corr_first))-
          np.sin(np.radians(phi))*
          np.cos(np.radians(dec_corr_first)))
        
    dec_corr_error=np.sqrt((dec_corr_first_error)**2+
                           (term*TF_error)**2+
                           (TF*np.sin(np.radians(ha_corr_first*15))*
                            np.sin(np.radians(dec_corr_first))*
                            ha_corr_first_error*15.)**2+
                           (TF*(np.cos(np.radians(phi))*
                            np.cos(np.radians(ha_corr_first*15))*
                            np.cos(np.radians(dec_corr_first))-
                            np.sin(np.radians(phi))*
                            np.sin(np.radians(dec_corr_first)))*
                           dec_corr_first_error)**2
                          )
        
    print('TF[°]=',TF,'+-',TF_error,' with chi^2_red=',chi_2_red)
    
    return(ha_corr, ha_corr_error,
           dec_corr, dec_corr_error,
           TF, TF_error)


    
    
    
    
    



