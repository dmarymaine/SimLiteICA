# generate sky components for LiteBird sims
# generate CMB with a given input seed and input spectrum (with no B-modes i.e. r=0)
# get foregrounds components and sum them up with generated CMB for user defined frequency
# store CMB only and full components maps in a working folder

import healpy as hp
import numpy as np
import os
import logging

def getSkyComponent(iseed, iseed_noise, inputCl, freq, fwhm, tele, gal_dir, gal_base_name, nside, sens, workdir):
   log = logging.getLogger("healpy")
   log.setLevel(logging.CRITICAL)

   # take foreground alm
   alm_gal = hp.read_alm(f'{gal_dir}/{gal_base_name.format(tele,np.int32(freq))}',hdu=(1,2,3))

   # get dimension of alm [0] to have lmax
   ndim = len(alm_gal[0])
   lmax = hp.Alm.getlmax(ndim)

   # read input Cl spectrum and generate alm
   cl = hp.read_cl(inputCl)
   alm_cmb = hp.synalm(cl,lmax=lmax)

   # create and save pure un-smoothed CMB map
   map_cmb = hp.alm2map(alm_cmb,nside,pol=True,verbose=False)
   os.makedirs(os.path.join(workdir,"cmb"),exist_ok=True)
   hp.write_map(f'{workdir}/cmb/cmb_nobeam_ns{nside}_{iseed}.fits',map_cmb,
                overwrite=True,dtype=[np.float64,np.float64,np.float64])

   # create sky summing up cmb and gal
   alm_sky = alm_gal + alm_cmb

   # create noise map and get its alm
   npix = hp.nside2npix(nside)
   sens_nside = sens/hp.nside2resol(nside,arcmin=True)
   n = [np.random.normal(0,sens_nside*0.5,npix),np.random.normal(0,sens_nside,npix),np.random.normal(0,sens_nside,npix)]
   alm_noise =hp.map2alm(n,lmax=lmax,pol=True,use_pixel_weights=True,verbose=False) 

   alm_sky = alm_sky + alm_noise

   # compute fwhm for extra smoothing
   fwhm_smth = (71. - fwhm)/60.*np.pi/180.
   alm_smth = hp.smoothalm(alm_sky,fwhm=fwhm_smth,pol=True,verbose=False)

   # generate and save smoothed sky map
   map_smth = hp.alm2map(alm_smth,nside,pol=True,verbose=False)
   os.makedirs(os.path.join(workdir,"sky"),exist_ok=True)
   hp.write_map(f'{workdir}/sky/sky_{np.int32(freq)}_sm_ns{nside}_{iseed}.fits',map_smth,
                overwrite=True,dtype=[np.float64,np.float64,np.float64])

