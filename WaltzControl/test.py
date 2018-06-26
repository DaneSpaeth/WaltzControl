unformated_ra='12:34:56#'
if len(unformated_ra)==9:
    #Formating string output Right Ascension
    ra='{}h{}m{}s'.format(unformated_ra[0:2],
                         unformated_ra[3:5],
                         unformated_ra[6:8])
print(ra)

seconds=00.2456
seconds=round(float(seconds))
seconds='{:02}'.format(seconds)
print(seconds)