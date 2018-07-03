ha_float=0

ha_float_seconds=round(ha_float*3600)
(minutes,seconds)=divmod(ha_float_seconds,60)
(hours,minutes)=divmod(minutes,60)
ha='{:+03}h{:02}m{:02}s'.format(hours,minutes,seconds)

print(ha)
