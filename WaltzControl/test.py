ha_float=-11.1234

ha_float_seconds=round(ha_float*3600)
(minutes,seconds)=divmod(ha_float_seconds,60)
(hours,minutes)=divmod(minutes,60)
ha='{:+02}:{:02}:{:02}'.format(hours,minutes,seconds)

print(ha)
