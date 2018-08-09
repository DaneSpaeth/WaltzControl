import statistics as st
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints']=1
import numpy as np
np.set_printoptions(threshold=np.inf)
import math
import pathlib


   


def fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,term,
                      plot=True,ObservationDate='all'):

    # fits a general set of pointing terms to the residuals between
    # measured and calculated positions (ha: hour angle, dec: declination)
    # only one terms is modelled at each time

    # input:
    # pos_obs: tuples of (HA,DEC) observed (telescope coordinates), radians
    # pos_calc: tuples of (HA,DEC) calculated (apparent place), radians
    # ha: hour angle during the observation, radians
    # term: string with the term to model, e.g. term = ['IH']

    # optional input:
    # plot = True: plotting

    # the modeling follows the TPOINT recommendations by Patrick Wallace

    # default terms modeled for an equatorial mount:

    # IH: index error in HA
    # ID: index error in DEC
    # NP: non-perpendicularity of HA and DEC axes
    # CH: non-perpendicularity of DEC and pointing axes
    # ME: polar axis elevation error
    # MA: polar axis error east-west

    # possible additional terms to model for an equatorial mount

    # FO: fork flexure
    # DAF: declination axis flexure
    # HCES: HA centering error (sine component)
    # HCEC: HA centering error (cosine component)
    # DCES: DEC centering error (sine component)
    # DCEC: DEC centering error (cosine component)
    # DNP: dynamic non-perpendicularity
    # X2HC: cos(2h) term EW

    # those latter ones are not included yet at the current stage
   
    # take differences of coordinates (pointing displacements)
   
    #We want to be able to specify a certain 
    #Date of Observation and need to mask
    #the arrays for this purpose
    if ObservationDate != 'all':
        ha_calc=ha_calc[Date==ObservationDate]
        ha_obs=ha_obs[Date==ObservationDate]
        dec_calc=dec_calc[Date==ObservationDate]
        dec_obs=dec_obs[Date==ObservationDate]
  
    #Initial Differences between observed and calculated coordinates
    ha_diff = ha_obs - ha_calc
    dec_diff = dec_obs - dec_calc
   
    #Since all terms but ID should be first normalized to the same offset
    #the first correction should be applied to all 
   
    #Assuming errors -> 
    #Later they could be given as arguments to the function 
    #but now we will just assume them here
    #uncertainty of observed coord in degrees (chose 2 arcmin)
    uncertainty_obs=2./60. 
    #uncertainty of calculated coord in degrees (chose 0.1 arcmin)
    uncertainty_calc=0.1/60. 
   
    ha_obs_error=np.ones(len(ha_obs))*uncertainty_obs/15.
    dec_obs_error=np.ones(len(dec_obs))*uncertainty_obs
   
    ha_calc_error=np.ones(len(ha_calc))*uncertainty_calc/15.
    dec_calc_error=np.ones(len(dec_calc))*uncertainty_calc
    #Propagating errors for the differences
    ha_diff_error=np.sqrt(np.square(ha_obs_error)+np.square(ha_calc_error)) 
    dec_diff_error=np.sqrt(np.square(dec_obs_error)+np.square(dec_calc_error)) 
   
   
    #In these arrays we will store the corrected calculated values
    #We just need them to initially have the same values 
    #as the calculated coordinates
    ha_corr=ha_calc
    dec_corr=dec_calc
    
    
    ha_corr_error=ha_calc_error
    dec_corr_error=dec_calc_error
      
    #Fitting IH and ID (it now is always fitted)
    #We have to fit it for every observation date individually
    ###Should work but not tested yet
    if ObservationDate != 'all':
        #Fitting IH if we have picked only one date of observation 
        #(not much to worry about in this case)
        val = -np.mean(ha_diff)
        #Error as error of the mean (standarddeviation/sqrt(N))
        val_error=np.std(ha_diff)/(math.sqrt(len(ha_diff))) 
        
        #We have a Minus sign to maintain definition of IH 
        #but change correction in the right direction
        ha_corr = ha_calc-val 
        ha_corr_error=np.sqrt(np.square(ha_calc_error)+np.square(val_error))
        print('IH[h] at',ObservationDate,'=',round(val), '+-',val_error)
       
        #Fitting ID if we have picked only one date of observation 
        #(not much to worry about in this case)
        val = -st.mean(dec_diff)
        val_error=np.std(dec_diff)/(math.sqrt(len(dec_diff)))
        dec_corr = dec_calc-val
        dec_corr_error=np.sqrt(np.square(dec_calc_error)+np.square(val_error))
        print('ID[°] at',ObservationDate,'=',val,'+-',val_error)
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
           
            ###ha_corr needs to be changed each index individually 
            #since we want to have just one corrected ha in the end
            #We correct ha at each date
            ha_corr = ha_corr-val*(Date==element) 
            ha_corr_error=np.sqrt(np.square(ha_corr_error)+
                                  np.square(val_error*(Date==element)))
            print('IH[h] at',element,'=',round(val,4),'+-',round(val_error,4))
           
           #Fitting ID analogously
            val = -np.mean(dec_diff[Date==element])
            val_error=(np.std(dec_diff[Date==element])/
                       (math.sqrt(len(dec_diff[Date==element]))))
            dec_corr = dec_corr-val*(Date==element)
            dec_corr_error=(np.sqrt(np.square(dec_corr_error)+
                                    np.square(val_error*(Date==element))))
            print('ID[°] at',element,'=',round(val,4),'+-',round(val_error,4))
           
    #Calculate new corrected differences between observed coordinates and corrected calculated coordinates        
    ha_diff_corr = ha_obs - ha_corr
    dec_diff_corr = dec_obs - dec_corr
    
    
    ha_diff_corr_error=np.sqrt(np.square(ha_obs_error)+
                               np.square(ha_corr_error))
    dec_diff_corr_error=np.sqrt(np.square(dec_obs_error)+
                                np.square(dec_corr_error))
    
    #To avoid to correct twice (want intital values for ha_corr in second correction) (need it in MA, ME and all)
    dec_corr_first=dec_corr
    ha_corr_first=ha_corr
        
    dec_corr_error_first=dec_corr_error
    ha_corr_error_first=ha_corr_error
   
   #Fitting following Numerical Recipes by W. H. Press page 781 f.
    if term == 'CH' or term== 'all':
        sxx = sum((1/(np.cos(np.radians(dec_corr_first))))**2*
                  1/(ha_diff_corr_error)**2)
        sxy = sum(ha_diff_corr*(1/np.cos(np.radians(dec_corr_first)))*
                  1/(ha_diff_corr_error)**2)
        
        val = sxy/sxx
        CH=val
        #For calculating the error
        s=sum(1/(ha_diff_corr_error)**2)
        sx=sum((1/np.cos(np.radians(dec_corr_first)))/(ha_diff_corr_error)**2)
        Delta=s*sxx-sx**2
        
        CH_error=s/Delta
        
        #First calculate the error
        ha_corr_error=np.sqrt((ha_corr_error_first)**2+
                              (1/np.cos(np.radians(dec_corr_first))*CH_error)**2+
                              (val/(np.cos(np.radians(dec_corr_first)))**2*
                               np.sin(np.radians(dec_corr_first))*
                               dec_corr_error_first/15.)**2)
        #Need that for 'all'
        ha_corr_error_CH=ha_corr_error
        #Calculating the corrected coordinates
        ha_corr = ha_corr_first+val/np.cos(np.radians(dec_corr_first))
        dec_corr = dec_corr_first
        
        print('CH[h]=',val,'+-',CH_error)
      
    if term == 'NP' or term =='all':
        sxx = sum(np.tan(np.radians(dec_corr_first))**2*
                  1/(ha_diff_corr_error)**2)
        sxy = sum(ha_diff_corr*np.tan(np.radians(dec_corr_first))*
                  1/(ha_diff_corr_error)**2)

        val = sxy/sxx
        NP=val
        #For calculating the error
        s=sum(1/(ha_diff_corr_error)**2)
        sx=sum((np.tan(np.radians(dec_corr_first)))/(ha_diff_corr_error)**2)
        Delta=s*sxx-sx**2
        
        NP_error=s/Delta
        
        #First calculate the error
        ha_corr_error=np.sqrt((ha_corr_error_first)**2+
                              (np.tan(np.radians(dec_corr_first))*NP_error)**2+
                              (val/(np.cos(np.radians(dec_corr_first)))**2*
                               dec_corr_error_first/15.)**2)
        #Need that for 'all'
        ha_corr_error_NP=ha_corr_error
        
        ha_corr = ha_corr_first+val*np.tan(np.radians(dec_corr_first))
        dec_corr = dec_corr
        
        print('NP[h]=',val,'+-',NP_error)
      
    if term == 'MA'or term =='all':
        
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

        val = (sxyh+sxyd)/(sxxh+sxxd)
        MA=val
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
        
        ha_corr = (ha_corr_first-
                   val/15.*
                   np.cos(np.radians(15.*ha_corr_first))*
                   np.tan(np.radians(dec_corr_first)))
        dec_corr = dec_corr_first+val*np.sin(np.radians(ha_corr_first*15.))
        
        ha_corr_error=np.sqrt(ha_corr_error_first**2+
                             (-np.cos(np.radians(ha_corr_first*15.))*
                              np.tan(np.radians(dec_corr_first))*
                              MA_error/15.)**2+
                             (val/15.*
                              np.sin(np.radians(ha_corr_first*15.))*
                              np.tan(np.radians(dec_corr_first))*
                              ha_corr_error_first)**2+
                             (-val/15.*
                              np.cos(np.radians(ha_corr_first*15.))*
                              1/(np.cos(np.radians(dec_corr_first)))**2*
                              dec_corr_error_first/15.)**2)
        ha_corr_error_MA=ha_corr_error
        
        dec_corr_error=np.sqrt((dec_corr_error_first)**2+
                              (np.sin(np.radians(ha_corr_first*15.))*
                               MA_error)**2+
                              (val*np.cos(np.radians(ha_corr_first*15.))*
                               ha_corr_error_first*15.)**2)
        dec_corr_error_MA=dec_corr_error
        
        print('MA[°]=',val,'+-',MA_error)
   
    if term == 'ME' or term =='all':

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

        val = (sxyh+sxyd)/(sxxh+sxxd)
        ME=val
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
        
        ha_corr = (ha_corr_first+
                   val/15*
                   np.sin(np.radians(ha_corr_first*15.))*
                   np.tan(np.radians(dec_corr_first)))
        dec_corr = dec_corr_first+val*np.cos(np.radians(ha_corr_first*15.))
        
        ha_corr_error=np.sqrt(ha_corr_error_first**2+
                             (np.sin(np.radians(ha_corr_first*15.))*
                              np.tan(np.radians(dec_corr_first))*
                              ME_error/15.)**2+
                             (val/15.*np.cos(np.radians(ha_corr_first*15.))*
                              np.tan(np.radians(dec_corr_first))*
                              ha_corr_error_first)**2+
                             (val/15.*np.sin(np.radians(ha_corr_first*15.))*
                              1/(np.cos(np.radians(dec_corr_first)))**2*
                              dec_corr_error_first/15.)**2)
        ha_corr_error_ME=ha_corr_error
        
        dec_corr_error=np.sqrt((dec_corr_error_first)**2+
                              (np.cos(np.radians(ha_corr_first*15.))*
                               ME_error)**2+
                              (-val*np.sin(np.radians(ha_corr_first*15.))*
                               ha_corr_error_first*15.)**2)
        dec_corr_error_ME=dec_corr_error
        
    
        
        print('ME[°]=',val,'+-',ME_error)
      
    if term == 'all':
        ha_corr = (ha_corr_first+
                  CH/np.cos(np.radians(dec_corr_first))+
                  NP*np.tan(np.radians(dec_corr_first))+
                  -MA/15.*np.cos(np.radians(15.*ha_corr_first))*
                  np.tan(np.radians(dec_corr_first))+
                  ME/15*np.sin(np.radians(ha_corr_first*15.))*
                  np.tan(np.radians(dec_corr_first)))
        
        ha_corr_error=np.sqrt(ha_corr_error_first**2+
                              ha_corr_error_CH**2+
                              ha_corr_error_NP**2+
                              ha_corr_error_MA**2+
                              ha_corr_error_ME**2)
        
        dec_corr=(dec_corr_first+
                 MA*np.sin(np.radians(ha_corr_first*15.))+
                 val*np.cos(np.radians(ha_corr_first*15.)))
        
        dec_corr_error=np.sqrt(dec_corr_error_first**2+
                              dec_corr_error_MA**2+
                              dec_corr_error_ME**2)
    
      #Second array of differences with second corrections
    ha_diff_corr_sec = ha_obs - ha_corr
    ha_diff_corr_sec_error=np.sqrt(ha_obs_error**2+ha_corr_error**2)
    dec_diff_corr_sec = dec_obs - dec_corr
    dec_diff_corr_sec_error=np.sqrt(dec_obs_error**2+dec_corr_error**2)
   
    



# all fitting done, now start plotting

    if plot==True:
        
        plt.figure(1)
        plt.subplot(121)
        plt.plot(ha_obs,ha_calc,'bo',label='ha_calc')
        plt.plot(ha_obs,ha_corr,'rx',label='ha_corr')
        plt.plot(np.arange(-12,12),np.arange(-12,12),'k')
        plt.xlabel('observed hour angle [h]')
        plt.ylabel('modeled hour angle [h]',labelpad=1)
        plt.ylim(-12,12)
        plt.xlim(-12,12)
        plt.legend(loc='best',numpoints=1)
      
        plt.subplot(122)
        plt.plot(dec_obs,dec_calc,'bo',label='dec_calc')
        plt.plot(dec_obs,dec_corr,'rx',label='dec_corr')
        plt.plot(np.arange(-10,90),np.arange(-10,90),'k')
        plt.xlabel('observed declination [deg]')
        plt.ylabel('modeled declination [deg]',labelpad=1)
        plt.legend(loc='best',numpoints=1)
      
        plt.show()
        #We also want to plot ha_diff and dec_diff 
        #vs ha and dec (for the moment ha_obs and dec_obs)
      
        #At first we create data 
        #to plot the Field of View of the Guidung Camera
        ha_space=np.linspace(ha_obs.min(),ha_obs.max())
        dec_space=np.linspace(dec_obs.min(),dec_obs.max())
        #If we only observe a specific date then we don't need to do much
        if ObservationDate != 'all':
        
        ### HA_Diff vs. HA_Obs ###
        
          #Plotting the original differences
            plt.figure()
            plt.subplot(221)
            plt.errorbar(ha_obs,ha_diff,yerr=ha_diff_error,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel('ha_diff = ha_obs-ha_calc [h]')
            #We also include a FOV area which is computed by 4'x 4' FOV of the guidung camera (4'=0.0044h=0.067°)
            plt.plot(ha_space,0.0022*np.ones(len(ha_space)),
                     color='black',label='FOV')
            plt.plot(ha_space,-0.0022*np.ones(len(ha_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('Initial Data')
          
          #Plotting the IH corrected differences
            plt.subplot(222)
            plt.errorbar(ha_obs,ha_diff_corr,yerr=ha_diff_corr_error,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel('ha_diff_corr = ha_obs-ha_corr [h]')
            #We also include a FOV area which is computed by 4'x 4' FOV of the guidung camera (4'=0.0044h=0.067°)
            plt.plot(ha_space,0.0022*np.ones(len(ha_space)),
                     color='black',label='FOV')
            plt.plot(ha_space,-0.0022*np.ones(len(ha_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('First Correction')
            
            #Plotting the second correction if the folowing terms are chosen 
            if term == 'CH' or term =='NP' or term =='MA' or term == 'ME'or term =='all' :
                plt.subplot(224)
                plt.errorbar(ha_obs,ha_diff_corr_sec,
                             yerr=ha_diff_corr_sec_error,
                             linestyle='none',marker='o',label=ObservationDate)
                plt.xlabel('observed hour angle [h]')
                plt.ylabel('ha_diff_corr_sec = ha_obs-ha_corr [h]')
                plt.title('Second Correction')
                plt.plot(ha_space,0.0022*np.ones(len(ha_space)),
                         color='black',label='FOV')
                plt.plot(ha_space,-0.0022*np.ones(len(ha_space)),color='black')
                plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
          
        
        ### HA_Diff vs. DEC_Obs ###
            plt.figure()
            plt.subplot(221)
            plt.errorbar(dec_obs, ha_diff,yerr=ha_diff_error,
                         linestyle='none',marker='o', label=ObservationDate)
            plt.xlabel('observed declination [°]')
            plt.ylabel('ha_diff = ha_obs-ha_calc [h]')
            plt.plot(dec_space,0.0022*np.ones(len(dec_space)),
                     color='black',label='FOV')
            plt.plot(dec_space,-0.0022*np.ones(len(dec_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('Initial Data')
            
            plt.subplot(222)
            plt.errorbar(dec_obs, ha_diff_corr,yerr=ha_diff_corr_error,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed declination [°]')
            plt.ylabel('ha_diff_corr = ha_obs-ha_corr [h]')
            plt.plot(dec_space,0.0022*np.ones(len(dec_space)),
                     color='black',label='FOV')
            plt.plot(dec_space,-0.0022*np.ones(len(dec_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('First Correction')
            
            #Second Correction: Plot only in these cases
            if (term == 'CH' or 
                term =='NP' or 
                term =='MA' or 
                term == 'ME' or 
                term =='all'):    
                plt.subplot(224)
                plt.errorbar(dec_obs,ha_diff_corr_sec,yerr=ha_diff_corr_error,
                             linestyle='none',marker='o',label=ObservationDate)
                plt.xlabel('observed declination[°]')
                plt.ylabel('ha_diff_corr_sec = ha_obs-ha_corr [h]')
                plt.title('Second Correction')
                plt.plot(dec_space,0.0022*np.ones(len(dec_space)),
                         color='black',label='FOV')
                plt.plot(dec_space,-0.0022*np.ones(len(dec_space)),
                         color='black')
                plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
          
        
        ### DEC_Diff vs. HA_Obs ###
        
            plt.figure()
            plt.subplot(221)
            plt.errorbar(ha_obs,dec_diff,yerr=dec_diff_error,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel('dec_diff = dec_obs-dec_calc [°]')
            plt.plot(ha_space,0.033*np.ones(len(ha_space)),
                     color='black',label='FOV')
            plt.plot(ha_space,-0.033*np.ones(len(ha_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('Initial Data')
            
            plt.subplot(222)
            plt.errorbar(ha_obs,dec_diff_corr,yerr=dec_diff_corr_error,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel('dec_diff_corr = dec_obs-dec_corr [°]')
            plt.plot(ha_space,0.033*np.ones(len(ha_space)),color='black',
                     label='FOV')
            plt.plot(ha_space,-0.033*np.ones(len(ha_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('First Correction')
            
            
            #Second Correction: Plot only in these cases
            if term =='MA' or term == 'ME'or term =='all':
                plt.subplot(224)
                plt.errorbar(ha_obs,dec_diff_corr_sec,
                             yerr=dec_diff_corr_sec_error,
                             linestyle='none',marker='o',label=ObservationDate)
                plt.xlabel('observed hour angle [h]')
                plt.ylabel('dec_diff_corr_sec = dec_obs-dec_corr [°]')
                plt.title('Second Correction')
                plt.plot(ha_space,0.033*np.ones(len(ha_space)),
                         color='black',label='FOV')
                plt.plot(ha_space,-0.033*np.ones(len(ha_space)),color='black')
                plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
        
        
        ### DEC_Diff vs. DEC_Obs ###
        
            plt.figure()
            plt.subplot(221)
            plt.errorbar(dec_obs,dec_diff,yerr=dec_diff_error,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed declination [°]')
            plt.ylabel('dec_diff = dec_obs-dec_calc [°]')
            plt.plot(dec_space,0.033*np.ones(len(dec_space)),
                     color='black',label='FOV')
            plt.plot(dec_space,-0.033*np.ones(len(dec_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('Initial Data')
            
            plt.subplot(222)
            plt.errorbar(dec_obs,dec_diff_corr,yerr=dec_diff_corr_error,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed declination [°]')
            plt.ylabel('dec_diff_corr = dec_obs-dec_corr [°]')
            plt.plot(dec_space,0.033*np.ones(len(dec_space)),
                     color='black',label='FOV')
            plt.plot(dec_space,-0.033*np.ones(len(dec_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('First Correction')
            
            
            #Second Correction: Plot only in these cases
            if term =='MA' or term == 'ME'or term =='all':
                plt.subplot(224)
                plt.errorbar(dec_obs,dec_diff_corr,yerr=dec_diff_error,
                             linestyle='none',marker='o',label=ObservationDate)
                plt.xlabel('observed declination [°]')
                plt.ylabel('dec_diff_corr = dec_obs-dec_corr [°]')
                plt.title('Second correction')
                plt.plot(dec_space,0.033*np.ones(len(dec_space)),
                         color='black',label='FOV')
                plt.plot(dec_space,-0.033*np.ones(len(dec_space)),
                         color='black')
                plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
            
            #Plotting as Field of View
        
            #Initital Data
            plt.figure()
            plt.subplot(221)
            plt.errorbar(dec_diff,15.*ha_diff,linestyle='none',
                         marker='.',label=ObservationDate)
            fig = plt.gcf()
            ax = fig.gca()
        
            circle1 = plt.Circle((0, 0), 0.0333, color='b',fill=False)
            ax.add_artist(circle1)
            plt.axis('scaled')
            plt.xlabel('Declination Difference [°]')
            plt.ylabel('Hour Angle Difference [°]')
            plt.title('Initial Data')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
           
            
            #First correction
            plt.subplot(222)
            plt.errorbar(dec_diff_corr,15.*ha_diff_corr,
                         linestyle='none',marker='.',label=ObservationDate)
            fig = plt.gcf()
            ax = fig.gca()
        
            circle1 = plt.Circle((0, 0), 0.0333, color='b',fill=False)
            ax.add_artist(circle1)
            plt.axis('scaled')
            plt.xlabel('Declination Difference [°]')
            plt.ylabel('Hour Angle Difference [°]')
            plt.title('First Correction')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            
            #Second Correction
            plt.subplot(224)
            plt.errorbar(dec_diff_corr_sec,15.*ha_diff_corr_sec,
                         linestyle='none',marker='.',label=ObservationDate)
            fig = plt.gcf()
            ax = fig.gca()
        
            circle1 = plt.Circle((0, 0), 0.0333, color='b',fill=False)
            ax.add_artist(circle1)
            plt.axis('scaled')
            plt.xlabel('Declination Difference [°]')
            plt.ylabel('Hour Angle Difference [°]')
            plt.title('Second Correction')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
            
        else: 
        #If we have all dates than we want to plot each date 
        #with a different color
        #unique makes an array of dates 
        #where each date only appears once, so looping over this array
        #and plotting all elements where the original date array 
        #is the unique date leads to different colors
          
            ### HA_DIFF VS- HA_OBS ###
            plt.figure()
            plt.subplot(221)
            for element in np.unique(Date): 
                plt.errorbar(ha_obs[Date==element],ha_diff[Date==element],
                             yerr=ha_diff_error[Date==element],
                             linestyle='none',marker='.',label=element)
            plt.xlabel('observed hour angle [h]')#
            plt.ylabel('ha_diff = ha_obs-ha_calc [h]')
            plt.title('Initial Data')
            #We also include a FOV area which is computed by 4'x 4' FOV of the guidung camera (4'=0.0044h=0.067°)
            plt.plot(ha_space,0.0022*np.ones(len(ha_space)),
                     color='black',label='FOV')
            plt.plot(ha_space,-0.0022*np.ones(len(ha_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            
            plt.subplot(222)
            for element in np.unique(Date): 
                plt.errorbar(ha_obs[Date==element],ha_diff_corr[Date==element],
                             yerr=ha_diff_corr_error[Date==element],
                             linestyle='none',marker='o',label=element)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel('ha_diff_corr = ha_obs-ha_corr [h]')
            plt.title('First correction')
            plt.plot(ha_space,0.0022*np.ones(len(ha_space)),
                     color='black',label='FOV')
            plt.plot(ha_space,-0.0022*np.ones(len(ha_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
          
          #Second Correction: Plot only in these cases
            if (term == 'CH' or
                term =='NP' or
                term =='MA' or
                term == 'ME' or
                term =='all'):
                plt.subplot(224)
                for element in np.unique(Date): 
                    plt.errorbar(ha_obs[Date==element],
                                 ha_diff_corr_sec[Date==element],
                                 yerr=ha_diff_corr_sec_error[Date==element],
                                 linestyle='none',marker='o',label=element)
                plt.xlabel('observed hour angle [h]')
                plt.ylabel('ha_diff_corr_sec = ha_obs-ha_corr [h]')
                plt.title('Second Correction'+' ('+term+')')
                plt.plot(ha_space,0.0022*np.ones(len(ha_space)),
                         color='black',label='FOV')
                plt.plot(ha_space,-0.0022*np.ones(len(ha_space)),color='black')
                plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
          
          ### HA_DIFF VS- DEC_OBS ###
            plt.figure()
            plt.subplot(221)
            for element in np.unique(Date):
                plt.errorbar(dec_obs[Date==element],ha_diff[Date==element],
                             yerr=ha_diff_error[Date==element],
                             linestyle='none',marker='o',label=element)
            plt.xlabel('observed declination [°]')
            plt.ylabel('ha_diff = ha_obs-ha_calc [h]')
            plt.title('Initial Data')
            plt.plot(dec_space,0.0022*np.ones(len(dec_space)),
                     color='black',label='FOV')
            plt.plot(dec_space,-0.0022*np.ones(len(dec_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            
            plt.subplot(222)
            for element in np.unique(Date):
                plt.errorbar(dec_obs[Date==element],
                             ha_diff_corr[Date==element],
                             yerr=ha_diff_corr_error[Date==element],
                             linestyle='none',marker='o',label=element)
            plt.xlabel('observed declination [°]')
            plt.ylabel('ha_diff_corr = ha_obs-ha_corr [h]')
            plt.title('First correction')
            plt.plot(dec_space,0.0022*np.ones(len(dec_space)),
                     color='black',label='FOV')
            plt.plot(dec_space,-0.0022*np.ones(len(dec_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
          
          #Second Correction: Plot only in these cases
            if (term == 'CH' or
                term =='NP' or
                term =='MA' or
                term == 'ME'or
                term =='all') :
                plt.subplot(224)
                for element in np.unique(Date): 
                    plt.errorbar(dec_obs[Date==element],
                                 ha_diff_corr_sec[Date==element],
                                 yerr=ha_diff_corr_error[Date==element],
                                 linestyle='none',marker='o',label=element)
                plt.xlabel('observed declination[°]')
                plt.ylabel('ha_diff_corr_sec = ha_obs-ha_corr [h]')
                plt.title('Second Correction'+' ('+term+')')
                plt.plot(dec_space,0.0022*np.ones(len(dec_space)),
                         color='black',label='FOV')
                plt.plot(dec_space,-0.0022*np.ones(len(dec_space)),
                         color='black')
                plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
              
        ###DEC_DIFF VS HA_OBS###
            plt.figure()
            plt.subplot(221)
            for element in np.unique(Date):
                plt.errorbar(ha_obs[Date==element],
                             dec_diff[Date==element],
                             yerr=dec_diff_error[Date==element],
                             linestyle='none',marker='o',label=element)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel('dec_diff = dec_obs-dec_calc [°]')
            plt.title('Initial Data')
            plt.plot(ha_space,0.033*np.ones(len(ha_space)),
                     color='black',label='FOV')
            plt.plot(ha_space,-0.033*np.ones(len(ha_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            
            plt.subplot(222)
            for element in np.unique(Date):
                plt.errorbar(ha_obs[Date==element],
                             dec_diff_corr[Date==element],
                             yerr=dec_diff_corr_error[Date==element],
                             linestyle='none',marker='o',label=element)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel('dec_diff_corr = dec_obs-dec_corr [°]')
            plt.title('First Correction')
            plt.plot(ha_space,0.033*np.ones(len(ha_space)),
                     color='black',label='FOV')
            plt.plot(ha_space,-0.033*np.ones(len(ha_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
          
          #Second Correction: Plot only in these cases
            if term =='MA' or term == 'ME'or term =='all':
                plt.subplot(224)
                for element in np.unique(Date):
                    plt.errorbar(ha_obs[Date==element],
                                 dec_diff_corr_sec[Date==element],
                                 yerr=dec_diff_corr_sec_error[Date==element],
                                 linestyle='none',marker='o',label=element)
                plt.xlabel('observed hour angle [h]')
                plt.ylabel('dec_diff_corr_sec = dec_obs-dec_corr [°]')
                plt.title('Second Correction'+' ('+term+')')
                plt.plot(ha_space,0.033*np.ones(len(ha_space)),
                         color='black',label='FOV')
                plt.plot(ha_space,-0.033*np.ones(len(ha_space)),color='black')
                plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
              
            ###DEC_DIFF VS DEC_OBS    
            plt.figure()
            plt.subplot(221)
            for element in np.unique(Date):
                plt.errorbar(dec_obs[Date==element],
                             dec_diff[Date==element],
                             yerr=dec_diff_error[Date==element],
                             linestyle='none',marker='o',label=element)
            plt.xlabel('observed declination [°]')
            plt.ylabel('dec_diff = dec_obs-dec_calc [°]')
            plt.title('Initial Data')
            plt.plot(dec_space,0.033*np.ones(len(dec_space)),
                     color='black',label='FOV')
            plt.plot(dec_space,-0.033*np.ones(len(dec_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            
            plt.subplot(222)
            for element in np.unique(Date):
                plt.errorbar(dec_obs[Date==element],
                             dec_diff_corr[Date==element],
                             yerr=dec_diff_corr_error[Date==element],
                             linestyle='none',marker='o',label=element)
            plt.xlabel('observed declination [°]')
            plt.ylabel('dec_diff_corr = dec_obs-dec_corr [°]')
            plt.title('First correction')
            plt.plot(dec_space,0.033*np.ones(len(dec_space)),
                     color='black',label='FOV')
            plt.plot(dec_space,-0.033*np.ones(len(dec_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            
          
          #Second Correction: Plot only in these cases
            if term =='MA' or term == 'ME'or term =='all':
                plt.subplot(224)
                for element in np.unique(Date):
                    plt.errorbar(dec_obs[Date==element],
                                 dec_diff_corr_sec[Date==element],
                                 yerr=dec_diff_error[Date==element],
                                 linestyle='none',marker='o',label=element)
                plt.xlabel('observed declination [°]')
                plt.ylabel('dec_diff_corr = dec_obs-dec_corr [°]')
                plt.title('Second correction'+' ('+term+')')
                plt.plot(dec_space,0.033*np.ones(len(dec_space)),
                         color='black',label='FOV')
                plt.plot(dec_space,-0.033*np.ones(len(dec_space)),
                         color='black')
                plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
           
        #Plotting as Field of View
        
            plt.figure()
            plt.subplot(221)
            for element in np.unique(Date):
                plt.errorbar(dec_diff[Date==element],
                             15.*ha_diff[Date==element],
                             linestyle='none',marker='.',label=element)
            fig = plt.gcf()
            ax = fig.gca()
        
            circle1 = plt.Circle((0, 0), 0.0333, color='b',fill=False)
            ax.add_artist(circle1)
            plt.axis('scaled')
            plt.xlabel('Declination Difference [°]')
            plt.ylabel('Hour Angle Difference [°]')
            plt.title('Initial Data')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            
            plt.subplot(222)
            for element in np.unique(Date):
                plt.errorbar(dec_diff_corr[Date==element],
                             15.*ha_diff_corr[Date==element],
                             linestyle='none',marker='.',label=element)
            fig = plt.gcf()
            ax = fig.gca()
        
            circle1 = plt.Circle((0, 0), 0.0333, color='b',fill=False)
            ax.add_artist(circle1)
            plt.axis('scaled')
            plt.xlabel('Declination Difference [°]')
            plt.ylabel('Hour Angle Difference [°]')
            plt.title('First Correction')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            
            plt.subplot(224)
            for element in np.unique(Date):
                plt.errorbar(dec_diff_corr_sec[Date==element],
                             15.*ha_diff_corr_sec[Date==element],
                             linestyle='none',marker='.',label=element)
            fig = plt.gcf()
            ax = fig.gca()
        
            circle1 = plt.Circle((0, 0), 0.0333, color='b',fill=False)
            ax.add_artist(circle1)
            plt.axis('scaled')
            plt.xlabel('Declination Difference [°]')
            plt.ylabel('Hour Angle Difference [°]')
            plt.title('Second Correction')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
            
    #return values   
    pfit = (ha_corr,dec_corr,val)
    return pfit
   
#Reading in Data
HIPnr=np.array([])
ha_calc=np.array([])
ha_obs=np.array([])
dec_calc=np.array([])
dec_obs=np.array([])
Date=np.array([])
#Choose the file here
#On Desktop (Dropbox)
current_path=pathlib.Path.cwd()
parrent_path=current_path.parent
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

readfile.close()

#We want to throw out data points which are too far off
#Not active right now
boolarray_ha=np.abs(ha_calc-ha_obs)<0.14
boolarray_dec=np.abs(dec_calc-dec_obs)<0.14
boolarray=np.logical_and(boolarray_ha,boolarray_dec)

HIPnr=HIPnr[boolarray]
ha_calc=ha_calc[boolarray]
ha_obs=ha_obs[boolarray]
dec_calc=dec_calc[boolarray]
dec_obs=dec_obs[boolarray]
Date=Date[boolarray]

#Test: We want hour angles between [0,24] instead of [-12,12]:
#ha_calc=ha_calc+24*(ha_calc<0)
#ha_obs=ha_obs+24*(ha_obs<0)
   
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'ID',plot=False,ObservationDate='2018-04-20')[2]
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'IH',plot=True,ObservationDate='2017-09-22')[2]

fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'ID',plot=True,ObservationDate='2018-07-18')[2]

#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'NP',plot=False,ObservationDate='2018-04-20')[2]
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'MA',plot=True,ObservationDate='2018-04-20')[2]
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'ME',plot=True,ObservationDate='2018-04-20')[2]

#print('values for 19.04')
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'ID',plot=False,ObservationDate='2018-04-19')[2]
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'IH',plot=False,ObservationDate='2018-04-19')[2]

#print('values for 17.10.2017')
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'ID',plot=False,ObservationDate='2017-10-17')[2]
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'IH',plot=True,ObservationDate='2017-10-17')[2]
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'CH',plot=False,ObservationDate='2017-10-17')[2]
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'NP',plot=True,ObservationDate='2017-10-17')[2]
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'NP',plot=True,ObservationDate='2017-10-17')[2]
#fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,'CH',plot=True,ObservationDate='2017-10-17')[2] 
