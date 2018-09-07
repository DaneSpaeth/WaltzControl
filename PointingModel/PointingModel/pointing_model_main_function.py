import statistics as st
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints']=1
import numpy as np
np.set_printoptions(threshold=np.inf)
import math
import pathlib

from pointing_model_functions import (apply_ID, apply_IH, apply_CH,
                                      apply_NP, apply_MA, apply_ME,
                                      apply_FO, apply_DCES, apply_DCEC,
                                      apply_DLIN, apply_TF) 

# fits a general set of pointing terms to the residuals between
# measured and calculated positions (ha: hour angle, dec: declination)
# only one terms is modelled at each time

# input:
# pos_obs: tuples of (HA,DEC) observed (telescope coordinates), radians
# pos_calc: tuples of (HA,DEC) calculated (apparent place), radians
# ha: hour angle during the observation, radians
# term: string with the term to model, e.g. term = ['IH']

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
   


def fit_pointing_term(ha_obs,ha_obs_error,
                      dec_obs,dec_obs_error,
                      ha_calc,dec_calc,Date,term,LST=None,
                      plot=True,ObservationDate='all'):


   
    #We want to be able to specify a certain 
    #Date of Observation and need to mask
    #the arrays for this purpose
    if ObservationDate != 'all':
        ha_calc=ha_calc[Date==ObservationDate]
        ha_obs=ha_obs[Date==ObservationDate]
        dec_calc=dec_calc[Date==ObservationDate]
        dec_obs=dec_obs[Date==ObservationDate]
        
    
    #Calculating and applying IH and ID
    (ha_diff, ha_diff_error,
     ha_corr, ha_corr_error,  
     ha_diff_corr, 
     ha_diff_corr_error)=apply_IH(ha_obs,ha_obs_error,ha_calc,
                                  Date,
                                  ObservationDate=ObservationDate)
     
    (dec_diff, dec_diff_error,
     dec_corr, dec_corr_error,  
     dec_diff_corr, 
     dec_diff_corr_error)=apply_ID(dec_obs,dec_obs_error,dec_calc,
                                   Date,
                                   ObservationDate=ObservationDate)
     
     
    
    #To avoid to correct twice (want intital values for ha_corr in second correction) (need it in MA, ME and all)
    dec_corr_first=dec_corr
    ha_corr_first=ha_corr
        
    dec_corr_first_error=dec_corr_error
    ha_corr_first_error=ha_corr_error
   
   #Fitting following Numerical Recipes by W. H. Press page 781 f.
    if term == 'CH' or term== 'all':
        (ha_corr, ha_corr_error,
         CH, CH_error, CH_correction) = apply_CH(ha_corr_first, 
                                                 ha_corr_first_error,
                                                 dec_corr_first, 
                                                 dec_corr_first_error,
                                                 ha_diff_corr,
                                                 ha_diff_corr_error)
         
        #Save for later use in different variable names
        #Need that for 'all'
        dec_corr = dec_corr_first
        dec_corr_error= dec_corr_first_error
        ha_corr_error_CH=ha_corr_error
      
    if term == 'NP' or term =='all':
        (ha_corr, ha_corr_error,
         NP, NP_error, NP_correction) = apply_NP(ha_corr_first, 
                                                 ha_corr_first_error,
                                                 dec_corr_first, 
                                                 dec_corr_first_error,
                                                 ha_diff_corr,
                                                 ha_diff_corr_error)
        
        #Need that for 'all'
        dec_corr = dec_corr_first
        dec_corr_error= dec_corr_first_error
        ha_corr_error_NP=ha_corr_error
        
    if term == 'MA'or term =='all':
        
        (ha_corr, ha_corr_error,
        dec_corr, dec_corr_error,
        MA, MA_error,
        MA_correction_ha,
        MA_correction_dec) = apply_MA(ha_corr_first, ha_corr_first_error,
                                      dec_corr_first, dec_corr_first_error,
                                      ha_diff_corr, ha_diff_corr_error,
                                      dec_diff_corr, dec_diff_corr_error)
        
        ha_corr_error_MA=ha_corr_error
        dec_corr_error_MA=dec_corr_error
   
    if term == 'ME' or term =='all':

        (ha_corr, ha_corr_error,
        dec_corr, dec_corr_error,
        ME, ME_error,
        ME_correction_ha,
        ME_correction_dec) = apply_ME(ha_corr_first, ha_corr_first_error,
                                      dec_corr_first, dec_corr_first_error,
                                      ha_diff_corr, ha_diff_corr_error,
                                      dec_diff_corr, dec_diff_corr_error)
        
        ha_corr_error_ME=ha_corr_error
        dec_corr_error_ME=dec_corr_error
        
    if term == 'FO' or term == 'all':
        (dec_corr, dec_corr_error,
         FO, FO_error,
         FO_correction) = apply_FO(ha_corr_first, 
                                   ha_corr_first_error,
                                   dec_corr_first, 
                                   dec_corr_first_error,
                                   dec_diff_corr,
                                   dec_diff_corr_error)
         
        #Need that for 'all'
        ha_corr = ha_corr_first
        ha_corr_error= ha_corr_first_error
        dec_corr_error_FO=dec_corr_error
        
    if term == 'DCES' or term == 'all':
        (dec_corr, dec_corr_error,
         DCES, DCES_error,
         DCES_correction) = apply_DCES(dec_corr_first,
                                       dec_corr_first_error,
                                       dec_diff_corr,
                                       dec_diff_corr_error)
         
        #Need that for 'all'
        ha_corr= ha_corr_first
        ha_corr_error= ha_corr_first_error
        dec_corr_error_DCES= dec_corr_error
        
    if term == 'DCEC' or term == 'all':
        (dec_corr, dec_corr_error,
         DCEC, DCEC_error,
         DCEC_correction) = apply_DCEC(dec_corr_first,
                                       dec_corr_first_error,
                                       dec_diff_corr,
                                       dec_diff_corr_error)
         
        #Need that for 'all'
        ha_corr= ha_corr_first
        ha_corr_error= ha_corr_first_error
        dec_corr_error_DCEC= dec_corr_error
        
    if term == 'DLIN' :
        (dec_corr, dec_corr_error,
         DLIN, DLIN_error,
         DLIN_correction) = apply_DLIN(dec_corr_first,
                                       dec_corr_first_error,
                                       dec_diff_corr,
                                       dec_diff_corr_error)
         
        #Need that for 'all'
        ha_corr= ha_corr_first
        ha_corr_error= ha_corr_first_error
        dec_corr_error_DLIN= dec_corr_error
        
    if term == 'TF' or term == 'all':
        (ha_corr, ha_corr_error,
         dec_corr, dec_corr_error,
         TF, TF_error,
         TF_correction_ha,
         TF_correction_dec) = apply_TF(ha_corr_first, ha_corr_first_error,
                                       dec_corr_first, dec_corr_first_error,
                                       ha_diff_corr, ha_diff_corr_error,
                                       dec_diff_corr, dec_diff_corr_error)
        
        ha_corr_error_TF=ha_corr_error
        dec_corr_error_TF=dec_corr_error
        
         
         

    if term == 'all':
        
        ha_corr = (ha_corr_first +
                   CH_correction +
                   NP_correction +
                   MA_correction_ha +
                   ME_correction_ha + 
                   TF_correction_ha)
        
        ha_corr_error=np.sqrt(ha_corr_first_error**2+
                              ha_corr_error_CH**2+
                              ha_corr_error_NP**2+
                              ha_corr_error_MA**2+
                              ha_corr_error_ME**2+
                              ha_corr_error_TF**2)
        
        dec_corr=(dec_corr_first +
                  MA_correction_dec +
                  ME_correction_dec +
                  DCES_correction +
                  DCEC_correction +
                  FO_correction +
                  TF_correction_dec)
        
        dec_corr_error=np.sqrt(dec_corr_first_error**2+
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
            plt.errorbar(ha_obs,ha_diff*60,yerr=ha_diff_error*60,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel('ha_diff = ha_obs-ha_calc [min]')
            #We also include a FOV area which is computed by 4'x 4' FOV of the guidung camera (4'=0.0044h=0.067°)
            plt.plot(ha_space,0.0022*np.ones(len(ha_space))*60,
                     color='black',label='FOV')
            plt.plot(ha_space,-0.0022*np.ones(len(ha_space))*60,color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('Initial Data')
          
          #Plotting the IH corrected differences
            plt.subplot(222)
            plt.errorbar(ha_obs,ha_diff_corr*60,yerr=ha_diff_corr_error*60,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel('ha_diff_corr = ha_obs-ha_corr [min]')
            #We also include a FOV area which is computed by 4'x 4' FOV of the guidung camera (4'=0.0044h=0.067°)
            plt.plot(ha_space,0.0022*np.ones(len(ha_space))*60,
                     color='black',label='FOV')
            plt.plot(ha_space,-0.0022*np.ones(len(ha_space))*60,color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('First Correction')
            
            #Plotting the second correction if the folowing terms are chosen 
            if (term == 'CH' or
                term == 'NP' or
                term == 'MA' or
                term == 'ME' or
                term == 'TF' or
                term =='all') :
                plt.subplot(224)
                plt.errorbar(ha_obs,ha_diff_corr_sec*60,
                             yerr=ha_diff_corr_sec_error*60,
                             linestyle='none',marker='o',label=ObservationDate)
                plt.xlabel('observed hour angle [h]')
                plt.ylabel('ha_diff_corr_sec = ha_obs-ha_corr [min]')
                plt.title('Second Correction')
                plt.plot(ha_space,0.0022*np.ones(len(ha_space))*60,
                         color='black',label='FOV')
                plt.plot(ha_space,-0.0022*np.ones(len(ha_space))*60,color='black')
                #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
          
        
        ### HA_Diff vs. DEC_Obs ###
            plt.figure()
            plt.subplot(221)
            plt.errorbar(dec_obs, ha_diff*60,yerr=ha_diff_error*60,
                         linestyle='none',marker='o', label=ObservationDate)
            plt.xlabel('observed declination [°]')
            plt.ylabel('ha_diff = ha_obs-ha_calc [min]')
            plt.plot(dec_space,0.0022*np.ones(len(dec_space))*60,
                     color='black',label='FOV')
            plt.plot(dec_space,-0.0022*np.ones(len(dec_space))*60,color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('Initial Data')
            
            plt.subplot(222)
            plt.errorbar(dec_obs, ha_diff_corr*60,yerr=ha_diff_corr_error*60,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed declination [°]')
            plt.ylabel('ha_diff_corr = ha_obs-ha_corr [min]')
            plt.plot(dec_space,0.0022*np.ones(len(dec_space))*60,
                     color='black',label='FOV')
            plt.plot(dec_space,-0.0022*np.ones(len(dec_space))*60,color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('First Correction')
            
            #Second Correction: Plot only in these cases
            if (term == 'CH' or 
                term =='NP' or 
                term =='MA' or 
                term == 'ME' or
                term == 'TF' or
                term =='all'):    
                plt.subplot(224)
                plt.errorbar(dec_obs,ha_diff_corr_sec*60,yerr=ha_diff_corr_error*60,
                             linestyle='none',marker='o',label=ObservationDate)
                plt.xlabel('observed declination[°]')
                plt.ylabel('ha_diff_corr_sec = ha_obs-ha_corr [min]')
                plt.title('Second Correction')
                plt.plot(dec_space,0.0022*np.ones(len(dec_space))*60,
                         color='black',label='FOV')
                plt.plot(dec_space,-0.0022*np.ones(len(dec_space))*60,
                         color='black')
                #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
          
        
        ### DEC_Diff vs. HA_Obs ###
        
            plt.figure()
            plt.subplot(221)
            plt.errorbar(ha_obs,dec_diff*60,yerr=dec_diff_error*60,
                         linestyle='none',marker='o',
                         label=ObservationDate)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel("dec_diff = dec_obs-dec_calc [']")
            plt.plot(ha_space,0.033*np.ones(len(ha_space))*60,
                     color='black',label='FOV')
            plt.plot(ha_space,-0.033*np.ones(len(ha_space))*60,
                     color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('Initial Data')
            
            plt.subplot(222)
            plt.errorbar(ha_obs,dec_diff_corr*60,yerr=dec_diff_corr_error*60,
                         linestyle='none',marker='o',
                         label=ObservationDate)
            plt.xlabel('observed hour angle [h]')
            plt.ylabel("dec_diff_corr = dec_obs-dec_corr [']")
            plt.plot(ha_space,0.033*np.ones(len(ha_space))*60,
                     color='black',
                     label='FOV')
            plt.plot(ha_space,-0.033*np.ones(len(ha_space))*60,
                     color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('First Correction')
            
            
            #Second Correction: Plot only in these cases
            if (term == 'MA' or 
                term == 'ME' or 
                term == 'FO' or 
                term == 'DCES' or
                term == 'DCEC' or
                term == 'DLIN' or
                term == 'TF' or
                term =='all'):
                plt.subplot(224)
                plt.errorbar(ha_obs,dec_diff_corr_sec*60,
                             yerr=dec_diff_corr_sec_error*60,
                             linestyle='none',marker='o',
                             label=ObservationDate)
                plt.xlabel('observed hour angle [h]')
                plt.ylabel("dec_diff_corr_sec = dec_obs-dec_corr [']")
                plt.title('Second Correction')
                plt.plot(ha_space,0.033*np.ones(len(ha_space))*60,
                         color='black',label='FOV')
                plt.plot(ha_space,-0.033*np.ones(len(ha_space))*60,
                         color='black')
                #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
        
        
        ### DEC_Diff vs. DEC_Obs ###
        
            plt.figure()
            plt.subplot(221)
            plt.errorbar(dec_obs,dec_diff*60,yerr=dec_diff_error*60,
                         linestyle='none',marker='o',
                         label=ObservationDate)
            plt.xlabel('observed declination [°]')
            plt.ylabel("dec_diff = dec_obs-dec_calc [']")
            plt.plot(dec_space,0.033*np.ones(len(dec_space))*60,
                     color='black',label='FOV')
            plt.plot(dec_space,-0.033*np.ones(len(dec_space))*60,color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('Initial Data')
            
            plt.subplot(222)
            plt.errorbar(dec_obs,dec_diff_corr*60,yerr=dec_diff_corr_error*60,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed declination [°]')
            plt.ylabel("dec_diff_corr = dec_obs-dec_corr [']")
            plt.plot(dec_space,0.033*np.ones(len(dec_space))*60,
                     color='black',label='FOV')
            plt.plot(dec_space,-0.033*np.ones(len(dec_space))*60,color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('First Correction')
            
            
            #Second Correction: Plot only in these cases
            if (term == 'MA' or 
                term == 'ME' or
                term == 'FO' or
                term == 'DCES' or
                term == 'DCEC' or
                term == 'DLIN' or
                term == 'TF' or
                term =='all'):
                plt.subplot(224)
                plt.errorbar(dec_obs,dec_diff_corr_sec*60,yerr=dec_diff_corr_sec_error*60,
                             linestyle='none',marker='o',
                             label=ObservationDate)
                plt.xlabel('observed declination [°]')
                plt.ylabel("dec_diff_corr = dec_obs-dec_corr [']")
                plt.title('Second correction')
                plt.plot(dec_space,0.033*np.ones(len(dec_space))*60,
                         color='black',label='FOV')
                plt.plot(dec_space,-0.033*np.ones(len(dec_space))*60,
                         color='black')
                #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
            
            #Plotting as Field of View
        
            #Initital Data
            plt.figure()
            plt.subplot(221)
            plt.errorbar(dec_diff*60,15.*ha_diff*60,linestyle='none',
                         marker='.',label=ObservationDate)
            fig = plt.gcf()
            ax = fig.gca()
        
            circle1 = plt.Circle((0, 0), 0.0333*60, color='b',fill=False)
            ax.add_artist(circle1)
            plt.axis('scaled')
            plt.xlabel("Declination Difference [']")
            plt.ylabel("Hour Angle Difference [']")
            plt.title('Initial Data')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
           
            
            #First correction
            plt.subplot(222)
            plt.errorbar(dec_diff_corr*60,15.*ha_diff_corr*60,
                         linestyle='none',marker='.',label=ObservationDate)
            fig = plt.gcf()
            ax = fig.gca()
        
            circle1 = plt.Circle((0, 0), 0.0333*60, color='b',fill=False)
            ax.add_artist(circle1)
            plt.axis('scaled')
            plt.xlabel("Declination Difference [']")
            plt.ylabel("Hour Angle Difference [']")
            plt.title('First Correction')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            
            #Second Correction
            plt.subplot(224)
            plt.errorbar(dec_diff_corr_sec*60,15.*ha_diff_corr_sec*60,
                         linestyle='none',marker='.',label=ObservationDate)
            fig = plt.gcf()
            ax = fig.gca()
        
            circle1 = plt.Circle((0, 0), 0.0333*60, color='b',fill=False)
            ax.add_artist(circle1)
            plt.axis('scaled')
            plt.xlabel("Declination Difference [']")
            plt.ylabel("Hour Angle Difference [']")
            plt.title('Second Correction')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
            

            #Differences vs Time
            plt.figure()
            plt.subplot(121)
            plt.errorbar(LST,ha_diff*60,yerr=ha_diff_error*60,
                     linestyle='none',marker='o')
            plt.ylabel('Hour Angle Difference [min] (not corr)')
            plt.xlabel('LST [h]')
            
            
            plt.subplot(122)
            plt.errorbar(LST,dec_diff*60,yerr=dec_diff_error*60,
                     linestyle='none',marker='o')
            plt.ylabel("Declination Difference ['] (not corr)")
            plt.xlabel('LST [h]')
            
            plt.show()
            
            #Differences vs Time
            plt.figure()
            plt.subplot(121)
            plt.errorbar(LST,ha_diff_corr_sec*60,yerr=ha_diff_corr_sec_error*60,
                     linestyle='none',marker='o')
            plt.ylabel("Hour Angle Difference [min] (2nd corr)")
            plt.xlabel('LST [h]')
            
            
            plt.subplot(122)
            plt.errorbar(LST,dec_diff_corr_sec*60,yerr=dec_diff_corr_sec_error*60,
                     linestyle='none',marker='o')
            plt.ylabel("Declination Difference ['] (2nd corr)")
            plt.xlabel('LST [h]')
            
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
                term == 'TF' or
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
                term == 'TF' or
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
            if (term == 'MA' or
                term == 'ME' or
                term == 'FO' or
                term == 'DCES' or
                term == 'DCEC' or
                term == 'DLIN' or
                term == 'TF' or
                term =='all'):
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
            if (term == 'MA' or
                term == 'ME' or
                term == 'FO' or
                term == 'DCES' or
                term == 'DCEC' or
                term == 'DLIN' or
                term == 'TF' or
                term =='all'):
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
    pfit = (ha_corr,dec_corr)
    return pfit 
