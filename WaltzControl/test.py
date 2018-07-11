import math

ha_float=-0.0001

hours=int(ha_float)
print(hours)
rest=abs(ha_float-hours)
print(rest)
minutes=int(rest*60)
print(minutes)
rest=abs(rest*60-minutes)
print(rest)
seconds=round(rest*60)
print(seconds)
print(hours,minutes,seconds)

sign=math.copysign(1,ha_float)
print(sign)