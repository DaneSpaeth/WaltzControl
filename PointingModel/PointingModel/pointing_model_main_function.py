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

from coord_operations import equ_to_altaz

from mpl_toolkits.mplot3d import Axes3D

# fits a general set of pointing terms to the residuals between
# measured and calculated positions (ha: hour angle, dec: declination)
# only one terms is modelled at each time

# input:
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
# TF: tube flexure
# FO: fork flexure
# DCES: DEC centering error (sine component)
# DCEC: DEC centering error (cosine component)
# DLIN: DEC linear fit 

# possible additional terms to model for an equatorial mount


# DAF: declination axis flexure
# HCES: HA centering error (sine component)
# HCEC: HA centering error (cosine component)
# DNP: dynamic non-perpendicularity
# X2HC: cos(2h) term EW

# those latter ones are not included yet at the current stage
 
   


def fit_pointing_term(ha_obs, ha_obs_error,
                      dec_obs, dec_obs_error,
                      ha_calc, dec_calc,
                      Date, terms, LST=None,
                      plot=True, ObservationDate='all'):
    """Calculates Pointing term corrections. 
       Prints Results.
       Plots Results if chosen.
    
       Input:
       ha_ons, ha_obs_error
       (array of observed hour angles and erros)
       dec_obs, dec_obs_error
       (array of observed declinations and erros)
       ha_calc, dec_calc
       (arrays of calculated hour angle and declination)
       Date
       (array of observed dates)
       terms
       (list of terms to be fitted or 'all')
       LST=None
       (array of Local Sidereal Times
       plot=True
       (Boolean if Results should be plotted)
       ObservationDate
       (String of one Date that should be picked out of Date array or 'all')
    """
       
    #terms array is an arary of strings containing the chosen pointing terms
    #IH and ID are always fitted
    #Define which terms are fitted if input is 'all'
    if terms == 'all':
        terms = ['CH','NP','MA','ME','TF','FO','DCES','DCEC','DLIN']



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
    
    #Define empty lists in which corrections are stored
    ha_correction_list=[]
    dec_correction_list=[]
    
    ha_correction_error_list=[]
    dec_correction_error_list=[]
    
   
   #Fitting following Numerical Recipes by W. H. Press page 781 f.
    if 'CH' in terms:
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
        
        #Append CH_correction into correction list
        ha_correction_list.append(CH_correction)
        #And Error
        ha_correction_error_list.append(ha_corr_error_CH)
      
    if 'NP' in terms:
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
        
        #Append NP_correction into correction list
        ha_correction_list.append(NP_correction)
        #And Error
        ha_correction_error_list.append(ha_corr_error_NP)
        
    if 'MA' in terms:
        
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
        
        #Append MA_correction into correction list
        ha_correction_list.append(MA_correction_ha)
        dec_correction_list.append(MA_correction_dec)
        #And Errors
        ha_correction_error_list.append(ha_corr_error_MA)
        dec_correction_error_list.append(dec_corr_error_MA)
   
    if 'ME' in terms:

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
        
        #Append ME_correction into correction list
        ha_correction_list.append(ME_correction_ha)
        dec_correction_list.append(ME_correction_dec)
        #And Errors
        ha_correction_error_list.append(ha_corr_error_ME)
        dec_correction_error_list.append(dec_corr_error_ME)
        
    if 'FO' in terms:
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
        
        #Append FO_correction into correction list
        dec_correction_list.append(FO_correction)
        #And Errors
        dec_correction_error_list.append(dec_corr_error_FO)
        
    if 'DCES' in terms:
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
        
        #Append DCES_correction into correction list
        dec_correction_list.append(DCES_correction)
        #And Errors
        dec_correction_error_list.append(dec_corr_error_DCES)
        
    if 'DCEC' in terms:
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
        
        #Append DCEC_correction into correction list
        dec_correction_list.append(DCEC_correction)
        #And Errors
        dec_correction_error_list.append(dec_corr_error_DCEC)
        
    if 'DLIN' in terms :
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
        
        #Append DLIN_correction into correction list
        dec_correction_list.append(DLIN_correction)
        #And Errors
        dec_correction_error_list.append(dec_corr_error_DLIN)
        
    if 'TF' in terms:
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
        
        #Append TF_correction into correction list
        ha_correction_list.append(TF_correction_ha)
        dec_correction_list.append(TF_correction_dec)
        #And Errors
        ha_correction_error_list.append(ha_corr_error_TF)
        dec_correction_error_list.append(dec_corr_error_TF)
        
    #All fitting is done
    #Add corrections together
         
    #    
    ha_corr = ha_corr_first + sum(ha_correction_list)
    
    squared_ha_errors=[error**2 for error in ha_correction_error_list]
    ha_corr_error = np.sqrt(ha_corr_first_error**2+sum(squared_ha_errors))
        
    dec_corr = dec_corr_first + sum(dec_correction_list) 
    
    squared_dec_errors=[error**2 for error in dec_correction_error_list]    
    dec_corr_error=np.sqrt(dec_corr_first_error**2+sum(squared_dec_errors))
    
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
            plt.ylabel('ra_diff = ra_obs - ra_calc [min]')
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
            plt.ylabel('ra_diff_cor = ra_obs - ra_corr [min]')
            #We also include a FOV area which is computed by 4'x 4' FOV of the guidung camera (4'=0.0044h=0.067°)
            plt.plot(ha_space,0.0022*np.ones(len(ha_space))*60,
                     color='black',label='FOV')
            plt.plot(ha_space,-0.0022*np.ones(len(ha_space))*60,color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('First Correction')
            
            #Plotting the second correction if the folowing terms are chosen 
            if ('CH' in terms or
                'NP' in terms or
                'MA' in terms or
                'ME' in terms or
                'TF' in terms) :
                plt.subplot(224)
                plt.errorbar(ha_obs,ha_diff_corr_sec*60,
                             yerr=ha_diff_corr_sec_error*60,
                             linestyle='none',marker='o',label=ObservationDate)
                plt.xlabel('observed hour angle [h]')
                plt.ylabel('ra_diff_cor_sec = ra_obs - ra_corr [min]')
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
            plt.ylabel('ra_diff = ra_obs - ra_calc [min]')
            plt.plot(dec_space,0.0022*np.ones(len(dec_space))*60,
                     color='black',label='FOV')
            plt.plot(dec_space,-0.0022*np.ones(len(dec_space))*60,color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('Initial Data')
            
            plt.subplot(222)
            plt.errorbar(dec_obs, ha_diff_corr*60,yerr=ha_diff_corr_error*60,
                         linestyle='none',marker='o',label=ObservationDate)
            plt.xlabel('observed declination [°]')
            plt.ylabel('ra_diff_cor = ra_obs - ra_corr [min]')
            plt.plot(dec_space,0.0022*np.ones(len(dec_space))*60,
                     color='black',label='FOV')
            plt.plot(dec_space,-0.0022*np.ones(len(dec_space))*60,color='black')
            #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.title('First Correction')
            
            #Second Correction: Plot only in these cases
            if ('CH' in terms or
                'NP' in terms or
                'MA' in terms or
                'ME' in terms or
                'TF' in terms):    
                plt.subplot(224)
                plt.errorbar(dec_obs,ha_diff_corr_sec*60,yerr=ha_diff_corr_error*60,
                             linestyle='none',marker='o',label=ObservationDate)
                plt.xlabel('observed declination[°]')
                plt.ylabel('ra_diff_cor_sec = ra_obs - ra_corr [min]')
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
            if ('MA' in terms or 
                'ME' in terms or
                'FO' in terms or
                'DCES' in terms or
                'DCEC' in terms or
                'DLIN' in terms or
                'TF' in terms):
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
            if ('MA' in terms or 
                'ME' in terms or
                'FO' in terms or
                'DCES' in terms or
                'DCEC' in terms or
                'DLIN' in terms or
                'TF' in terms):
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
            
            #Scatter Plots: Area indicating error (first correction)
            #Plot Positive differences in blue, negatives in red
            dec_pos_bool = dec_diff_corr > 0
            dec_neg_bool = dec_diff_corr < 0
            ha_pos_bool = ha_diff_corr > 0
            ha_neg_bool = ha_diff_corr < 0
            
            dec_pos_sec_bool = dec_diff_corr_sec > 0
            dec_neg_sec_bool = dec_diff_corr_sec < 0
            ha_pos_sec_bool = ha_diff_corr_sec > 0
            ha_neg_sec_bool = ha_diff_corr_sec < 0
            
            
            
            
            
            plt.figure()
            plt.subplot(122)
            plt.scatter(ha_obs[dec_pos_bool], dec_obs[dec_pos_bool],
                        s=dec_diff_corr[dec_pos_bool]*1000,
                        color= 'blue')
            plt.scatter(ha_obs[dec_neg_bool], dec_obs[dec_neg_bool],
                        s=abs(dec_diff_corr[dec_neg_bool]*1000),
                        color= 'red')
            
            
            plt.ylabel('observed Declination [°]')
            plt.xlabel('observed Hour Angle [h]')
            plt.title('(1st) corrected Declination difference \n as markersize')
            
            plt.subplot(121)
            plt.scatter(ha_obs[ha_pos_bool], dec_obs[ha_pos_bool],
                        s=abs(ha_diff_corr[ha_pos_bool]*15*1000),
                        color='blue')
            plt.scatter(ha_obs[ha_neg_bool], dec_obs[ha_neg_bool],
                        s=abs(ha_diff_corr[ha_neg_bool]*15*1000),
                        color='red')
            
            plt.ylabel('observed Declination [°]')
            plt.xlabel('observed Hour Angle [h]')
            plt.title('(1st) corrected Hour Angle difference \n as markersize')
            
            plt.show()
            
            #Scatter Plots: Area indicating error (second correction)
            plt.figure()
            plt.subplot(122)
            plt.scatter(ha_obs[dec_pos_sec_bool], dec_obs[dec_pos_sec_bool],
                        s=dec_diff_corr_sec[dec_pos_sec_bool]*1000,
                        color= 'blue')
            plt.scatter(ha_obs[dec_neg_sec_bool], dec_obs[dec_neg_sec_bool],
                        s=abs(dec_diff_corr_sec[dec_neg_sec_bool]*1000),
                        color= 'red')
            
            plt.ylabel('observed Declination [°]')
            plt.xlabel('observed Hour Angle [h]')
            plt.title('(2nd) corrected Declination difference \n as markersize')
            
            plt.subplot(121)
            plt.scatter(ha_obs[ha_pos_sec_bool], dec_obs[ha_pos_sec_bool],
                        s=abs(ha_diff_corr_sec[ha_pos_sec_bool]*15*1000),
                        color='blue')
            plt.scatter(ha_obs[ha_neg_sec_bool], dec_obs[ha_neg_sec_bool],
                        s=abs(ha_diff_corr_sec[ha_neg_sec_bool]*15*1000),
                        color='red')
            
            plt.xlabel('observed Declination [°]')
            plt.ylabel('observed Hour Angle [h]')
            plt.title('(2nd) corrected Hour Angle difference \n as markersize')
            
            plt.show()
            
            #3D Plots: error vs positions
            
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(dec_obs,ha_obs,dec_diff_corr_sec)
            
            ax.set_xlabel('observed Declination [°]')
            ax.set_ylabel('observed Hour Angle [h]')
            ax.set_zlabel('dec_diff_corr_sec [°]')
            
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(dec_obs,ha_obs,ha_diff_corr_sec)
            
            ax.set_xlabel('observed Declination [°]')
            ax.set_ylabel('observed Hour Angle [h]')
            ax.set_zlabel('ha_diff_corr_sec [h]')
            
            plt.show()
            
            #Also plot difference in alt az 
            #and overplot diffraction correction
            
            #Calculate observed Alt and Az
            alt_obs, az_obs = equ_to_altaz(ha_obs, dec_obs)
            alt_calc, az_calc = equ_to_altaz(ha_calc, dec_calc)
            
            #Calculate corrected Alt and Az
            alt_corr_first, az_corr_first = equ_to_altaz(ha_corr_first,
                                                         dec_corr_first)
            alt_corr, az_corr = equ_to_altaz(ha_corr, dec_corr)
            
            #Calculate uncorrected alt difference
            alt_diff = alt_obs - alt_calc
            
            #Calculate corrected alt difference
            alt_diff_corr_first = alt_obs - alt_corr_first
            alt_diff_corr_sec = alt_obs - alt_corr
            
            def calc_refraction(alt):
                """Calculate refraction in arcminutes
                """
                #Choose temp and press
                temp = 15
                press = 97
                #Calculate temperature/pressure factor
                factor= press/101*283/(273+temp)
                #Calculate refraction in arcminutes
                R=(1/np.tan(np.radians(alt+7.31/(alt+4.4))))*factor
            
                return R
            
            #Create alt array
            alt_space=np.linspace(10,90,1000)
            
            #Plot
            
            plt.figure()
            plt.subplot(221)
            plt.plot(alt_obs,alt_diff*60,
                     linestyle='none',marker='.',
                     label=ObservationDate)
            plt.xlabel('observed altitude [°]')
            plt.ylabel("alt_diff = alt_obs-alt_calc [']")
            plt.title('Initial Data')
            plt.plot(alt_space,calc_refraction(alt_space),
                     color='red', label='refraction')
            
            plt.plot(alt_space,0.033*np.ones(len(alt_space))*60,
                     color='black',label='FOV')
            plt.plot(alt_space,-0.033*np.ones(len(alt_space))*60,
                     color='black')
            
            plt.subplot(222)
            plt.plot(alt_obs,alt_diff_corr_first*60,
                     linestyle='none',marker='.',
                     label=ObservationDate)
            plt.xlabel('observed altitude [°]')
            plt.ylabel("alt_diff = alt_obs-alt_calc [']")
            plt.title('First Correction')
            plt.plot(alt_space,calc_refraction(alt_space),
                     color='red', label='refraction')
            
            plt.plot(alt_space,0.033*np.ones(len(alt_space))*60,
                     color='black',label='FOV')
            plt.plot(alt_space,-0.033*np.ones(len(alt_space))*60,
                     color='black')
            
            plt.subplot(224)
            plt.plot(alt_obs,alt_diff_corr_sec*60,
                     linestyle='none',marker='.',
                     label=ObservationDate)
            plt.xlabel('observed altitude [°]')
            plt.ylabel("alt_diff_corr = alt_obs-alt_corr [']")
            plt.title('Second correction')
            plt.plot(alt_space,calc_refraction(alt_space),
                     color='red', label='refraction')
            
            plt.plot(alt_space,0.033*np.ones(len(alt_space))*60,
                     color='black',label='FOV')
            plt.plot(alt_space,-0.033*np.ones(len(alt_space))*60,
                     color='black')
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
            plt.ylabel('ra_diff = ra_obs - ra_calc [h]')
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
            plt.ylabel('ra_diff_cor = ra_obs - ra_corr [h]')
            plt.title('First correction')
            plt.plot(ha_space,0.0022*np.ones(len(ha_space)),
                     color='black',label='FOV')
            plt.plot(ha_space,-0.0022*np.ones(len(ha_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
          
          #Second Correction: Plot only in these cases
            if ('CH' in terms or
                'NP' in terms or
                'MA' in terms or
                'ME' in terms or
                'TF' in terms):
                plt.subplot(224)
                for element in np.unique(Date): 
                    plt.errorbar(ha_obs[Date==element],
                                 ha_diff_corr_sec[Date==element],
                                 yerr=ha_diff_corr_sec_error[Date==element],
                                 linestyle='none',marker='o',label=element)
                plt.xlabel('observed hour angle [h]')
                plt.ylabel('ra_diff_cor_sec = ra_obs - ra_corr [h]')
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
            plt.ylabel('ra_diff = ra_obs - ra_calc [h]')
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
            plt.ylabel('ra_diff_cor = ra_obs - ra_corr [h]')
            plt.title('First correction')
            plt.plot(dec_space,0.0022*np.ones(len(dec_space)),
                     color='black',label='FOV')
            plt.plot(dec_space,-0.0022*np.ones(len(dec_space)),color='black')
            plt.legend(loc="upper left", bbox_to_anchor=(1,1))
            plt.show()
          
          #Second Correction: Plot only in these cases
            if ('CH' in terms or
                'NP' in terms or
                'MA' in terms or
                'ME' in terms or
                'TF' in terms) :
                plt.subplot(224)
                for element in np.unique(Date): 
                    plt.errorbar(dec_obs[Date==element],
                                 ha_diff_corr_sec[Date==element],
                                 yerr=ha_diff_corr_error[Date==element],
                                 linestyle='none',marker='o',label=element)
                plt.xlabel('observed declination[°]')
                plt.ylabel('ra_diff_cor_sec = ra_obs - ra_corr [h]')
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
            if ('MA' in terms or 
                'ME' in terms or
                'FO' in terms or
                'DCES' in terms or
                'DCEC' in terms or
                'DLIN' in terms or
                'TF' in terms):
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
            if ('MA' in terms or 
                'ME' in terms or
                'FO' in terms or
                'DCES' in terms or
                'DCEC' in terms or
                'DLIN' in terms or
                'TF' in terms):
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
