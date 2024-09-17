import readInstData
import numpy as np

fwhm, sens, freq = readInstData.readInstData()

print (fwhm[0],fwhm[0]/60.)

gal_dir, gal_base_name, cmb_dir, cmb_spec_r0, cmb_spec_r1 = readInstData.readSkyData()

print (gal_dir, gal_base_name)

tele = "MFT"

print (gal_base_name.format(tele,np.int32(freq[4])))


