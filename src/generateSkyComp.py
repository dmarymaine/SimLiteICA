# generate sky components for LiteBird sims
# generate CMB with a given input seed and input spectrum (with no B-modes i.e. r=0)
# get foregrounds components and sum them up with generated CMB for user defined frequency
# store CMB only and full components maps in a working folder

import healpy as hp
import numpy as np


def getSkyComponent(iseed, inputCl, freq, fwhm, tele, gal_dir, gal_base_name, nside, workdir):

   # first generate CMB component:
   np.random.seed(iseed)
   cl = hp.read_cl(inputCl)
   map_cmb = hp.synfast(cl,nside,pol=True)

   # store CMB only map
   hp.write_map(f'{workdir}/cmb_nobeam_{iseed}_ns{nside}.fits',map_cmb)

   # take foreground alm
   alm_gal = hp.read_alm(f'{gal_dir}/{gal_base_name.format(tele,np.int32(freq))}',hdu=(1,2,3))

   # create map of foregrounds
   map_gal = hp.alm2map(alm_gal,nside,pol=True)

   # sum CMB and foregrounds and then smooth them to a common angular resolution
   map = map_cmb + map_gal
   fwhm_smth = (71. - fwhm)/60.*np.pi/180.
   map_smth = hp.smoothing(map,pol=True,fwhm=fwhm_smth)

   # save smoothed sky map
   hp.write_map(f'{workdir}/sky_{freq}_sm_ns{nside}_{iseed}.fits',map_smth)

