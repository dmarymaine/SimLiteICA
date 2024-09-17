# read instrument data from instr.dat
# data are organized in three vectors: freq, rms (uK/arcmin) and fwhm

import configparser

config = configparser.ConfigParser()
config.read("instr.ini")

fwhm = config.get("FWHM","fwhm_list")
sens = config.get("SENS","sens_list")
freq = config.get("FREQ","freq_list")

print (fwhm)
print (sens)
print (freq)



