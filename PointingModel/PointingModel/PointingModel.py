from pointing_model_functions import reading_in_data, fit_pointing_term

HIPnr, ha_calc, ha_obs, dec_calc, dec_obs, Date, LST = reading_in_data(refr_corr=False)

fit_pointing_term(ha_obs,dec_obs,ha_calc,dec_calc,Date,'all',LST=LST,plot=True,ObservationDate='2018-07-18')[2]
