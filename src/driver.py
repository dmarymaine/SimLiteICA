
# Copyright (c) 2024 by the parties listed in the AUTHORS file.
# All rights reserved. The use of this code is governed by free
# open source license.

"""
This scripts runs sky (gal + cmb) simulations for an experiment like LiteBird.

Galactic emission alms are supposed to be already computed.

It generates MC realisations of CMB sky as well as instrumental isotropic
white noise.

In addition you can supply simulations with:
    - gain mismatch among frequency channels
    - residual from sidelobe simulations

Frequency maps created are then ingested by FastICA component separation
code in order to retrieve 'pure' CMB signal where to evaluate the
actual residual of systematics in the CMB map
"""

import os
import sys
import traceback
import argparse
from mpi4py import MPI
import healpy as hp
import pylab
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

import readInstData
import generateSkyComp

mpl.style.use('classic')

def parse_arguments():
   # parge arguments from input parameter file
   parser = argparse.ArgumentParser(
     description="Simulate frequency maps for a specified experiment to be processed by FastICA.")

   parser.add_argument(
       "--workdir", required=False, default="workdir",help="output/working directory"
   )

   parser.add_argument(
       "--inst_file", required=True,default=None,help="Config file with sections [FREQ,TELE,FWHM,SENS,GAIN] that "
       "specify the simulated experiments. It assumes that foreground maps at the specified elements in FREQ and TELE"
       "actually exist"
   )

   parser.add_argument(
       "--data_file", required=True,default=None,help="Config file with sections [GALALM,CMB,SIMDATA] where "
       "location of galactic emission data, CMB power spectrum are actually stored"
   )

   try:
      args = parser.parse_args()
   except SystemExit:
      sys.exit()

   return args

def main():

  args = parse_arguments()

  os.makedirs(args.workdir,exist_ok=True)
  print (f"Logger: workdir {args.workdir} created")

  fwhm, sens, freq, gain, tele = readInstData.readInstData(args.inst_file)
  print (f"Logger: instrument properties are loaded from {args.inst_file}")

  gal_dir, gal_base_name, cmb_dir, cmb_spec_r0, cmb_spec_r1, nside = readInstData.readSkyData(args.data_file)
  print (f"Logger: galdir, alm and cmb data specified from {args.data_file}")


  print (f'{gal_base_name}'.format(tele[4],np.int32(freq[4])))


  inputCl=f'{cmb_dir}{cmb_spec_r0}'

  generateSkyComp.getSkyComponent(10,inputCl,freq[0], fwhm[0], tele[0], gal_dir, gal_base_name, np.int32(nside), './')


  cmb=hp.read_map("cmb_nobeam_ns256_10.fits",field=(0,1,2))
  sky=hp.read_map("sky_40.0_sm_ns256_10.fits",field=(0,1,2))
  hp.mollview(cmb[0],norm='hist')
  hp.mollview(np.sqrt(sky[1]*sky[1]+sky[2]*sky[2]),norm='hist')
  plt.show()


if __name__ == "__main__":
   try:
      main()
   except Exception:
       # we have an unhandled exception on at least one process. Print a stack
       # trace for this process and then abort so that all processes terminate.
       mpiworld = MPI.COMM_WORLD
       rank = mpiworld.Get_rank()
       procs = mpiworld.Get_size()
       if procs == 1:
         raise
       exc_type, exc_value, exc_traceback = sys.exc_info()
       lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
       lines = ["Proc {}: {}".format(rank, x) for x in lines]
       print("".join(lines), flush=True)
       if mpiworld is not None:
           mpiworld.Finalize()
