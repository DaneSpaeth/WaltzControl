from pointing_model_functions import reading_in_data, fit_pointing_term, apply_IH

(HIPnr, ha_calc, ha_obs, ha_obs_error, 
 dec_calc, dec_obs, dec_obs_error, Date, LST) = reading_in_data(refr_corr=True)

fit_pointing_term(ha_obs,ha_obs_error,
                  dec_obs,dec_obs_error,
                  ha_calc,dec_calc,Date,'all',LST=LST,plot=False,ObservationDate='2018-07-18')

#apply_ID(dec_obs,dec_obs_error,ha_calc,Date,ObservationDate='2018-07-18')
#apply_IH(ha_obs,ha_obs_error,ha_calc,Date,ObservationDate='all')

