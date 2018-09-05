def apply_ME(ha_corr_first, ha_corr_first_error,
             dec_corr_first, dec_corr_first_error,
             ha_diff_corr, ha_diff_corr_error,
             dec_diff_corr, dec_diff_corr_error):
    """Calculates ME correction.
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
               (MEue of MA and error)
    """
    
    #We calculate MA and Me in degree. 
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

    ME= (sxyh+sxyd)/(sxxh+sxxd)
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
               ME/15*
               np.sin(np.radians(ha_corr_first*15.))*
               np.tan(np.radians(dec_corr_first)))
    dec_corr = dec_corr_first+ME*np.cos(np.radians(ha_corr_first*15.))
        
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
    ha_corr_error_ME=ha_corr_error
        
    dec_corr_error=np.sqrt((dec_corr_first_error)**2+
                           (np.cos(np.radians(ha_corr_first*15.))*
                            ME_error)**2+
                           (-ME*np.sin(np.radians(ha_corr_first*15.))*
                            ha_corr_first_error*15.)**2)
    dec_corr_error_ME=dec_corr_error
        
    
        
    print('ME[°]=',ME,'+-',ME_error)
    
    return(ha_corr, ha_corr_error,
           dec_corr, dec_corr_error,
           ME, ME_error)