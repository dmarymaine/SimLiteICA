import readInstData
import generateSkyComp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('classic')

fwhm, sens, freq, gain, tele = readInstData.readInstData()

print (fwhm[0],fwhm[0]/60., freq[10],gain[10])

gal_dir, gal_base_name, cmb_dir, cmb_spec_r0, cmb_spec_r1, nside = readInstData.readSkyData()

print (gal_dir, gal_base_name)


print (f'{gal_base_name}'.format(tele[4],np.int32(freq[4])))


inputCl=f'{cmb_dir}{cmb_spec_r0}'

generateSkyComp.getSkyComponent(10,inputCl,freq[0], fwhm[0], tele[0], gal_dir, gal_base_name, np.int32(nside), './')


hp.read_map("cmb_nobeam_10_ns256.fits",field=(0,1,2))

