from coord_operations import equ_to_altaz, altaz_to_equ


alt,az,_,__=equ_to_altaz(11,-10)
print(alt,az)

ha,dec=altaz_to_equ(alt,az)
print(ha,dec)




