hip_nr='1'
try:
    hip_nr=int(hip_nr)
    hip_pointing="{:06d}".format(hip_nr)
    print(hip_pointing)
    print(type(hip_pointing))
except ValueError:
    print('Invalid Hiparcos number')
