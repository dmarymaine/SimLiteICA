
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
import warnings
import readInstData
import generateSkyComp
import Logging as log

mpl.style.use('classic')
warnings.filterwarnings("ignore")

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

   parser.add_argument(
       "--nmc",required=True,default=None,help="Number of MC simulations (both CMB and noise) to be done"
   )

   parser.add_argument(
       "--seed",required=False,default=100,help="Starting seed for MC realisation of CMB and noise"
   )


   parser.add_argument(
       "--debug",required=False,default=False,help="More verbosity and checks in debug mode"
   )

   try:
      args = parser.parse_args()
   except SystemExit:
      sys.exit()

   return args


logger = log.getLogger('DriverMain')

def main():

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    procs = comm.Get_size()

    if (rank == 0) :
       log.logHeader()
       logger.info('Entering the main method (driver)')

    args = parse_arguments()

    if (rank == 0) :
       os.makedirs(args.workdir,exist_ok=True)
       logger.info(f'Work directory {args.workdir} has been created')

    comm.Barrier()
    fwhm, sens, freq, gain, tele = readInstData.readInstData(args.inst_file)

    if (rank == 0) :
       logger.info(f'Instrument properies has been loaded from {args.inst_file}')

    gal_dir, gal_base_name, cmb_dir, cmb_spec_r0, cmb_spec_r1, nside = readInstData.readSkyData(args.data_file)

    if (rank == 0):
       logger.info(f'Gal directory, alm and cmb data loaded from {args.data_file}')

    inputCl=f'{cmb_dir}{cmb_spec_r0}'

    # first half of the script: generate sky components (cmb + gal) and store them
    iseed_cmb = args.seed
    iseed_noise = iseed_cmb + 1000*len(freq)

    if (rank == 0) :
      logger.info("Start MC creation map")

    # now divide the workload among the processors
    nfreq = len(freq)
    nfreq_per_cpu = np.int32(nfreq / procs)
    myindex = np.arange(rank*nfreq_per_cpu,rank*nfreq_per_cpu+nfreq_per_cpu)

    for inmc in range(np.int32(args.nmc)):

       # cmb has to be the same for all frequencies
       iseed_cmb = iseed_cmb + inmc

       if (rank == 0) :
          logger.info(f"generating sim {inmc+1} of {np.int32(args.nmc)}")
       # this generates unsmoothed CMB + smoothed full sky frequency maps and store them into
       # workdir/cmb and workdir/sky

       # loop over frequencies listed in freq
       myfreq = freq[myindex[0]:myindex[0]+nfreq_per_cpu]
       myfwhm = fwhm[myindex[0]:myindex[0]+nfreq_per_cpu]
       mytele = tele[myindex[0]:myindex[0]+nfreq_per_cpu]
       mysens = sens[myindex[0]:myindex[0]+nfreq_per_cpu]

       if (rank == 0):
          logger.info(f"iseed_cmb = {iseed_cmb} for MC {inmc}")
       for fr,res,tel,sen in zip(myfreq,myfwhm,mytele,mysens):
          generateSkyComp.getSkyComponent(iseed_cmb,iseed_noise,inputCl,fr, res, tel,
                                       gal_dir, gal_base_name, np.int32(nside),sen,args.workdir)

          # noise should be independent among frequency channels
          iseed_noise = iseed_noise + inmc


    # wait for all processor to finish
    comm.Barrier()
    if (rank == 0) :
       logger.info("Maps have been created")

    if (args.debug and rank == 0) :
      logger.debug("Here is a sample one")
      cmb=hp.read_map(f"{args.workdir}/cmb/cmb_nobeam_ns{nside}_{iseed_cmb-1}.fits",field=(0,1,2))
      sky=hp.read_map(f"{args.workdir}/sky/sky_{np.int32(freq[7])}_sm_ns{nside}_{iseed_cmb-1}.fits",field=(0,1,2))
      hp.mollview(cmb[0],norm='hist')
      hp.mollview(np.sqrt(sky[1]*sky[1]+sky[2]*sky[2]),norm='hist')
      plt.show(block=True)
      plt.pause(0.001)

    if (rank == 0):
      log.logFooter()

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
