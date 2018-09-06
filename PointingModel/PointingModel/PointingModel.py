from pointing_model_main_function import fit_pointing_term
from pointing_model_functions import reading_in_data

(HIPnr, ha_calc, ha_obs, ha_obs_error, 
 dec_calc, dec_obs, dec_obs_error, Date, LST) = reading_in_data(refr_corr=True)

fit_pointing_term(ha_obs,ha_obs_error,
                  dec_obs,dec_obs_error,
                  ha_calc,dec_calc,Date,'DCEC',LST=LST,plot=True,ObservationDate='2018-07-18')



