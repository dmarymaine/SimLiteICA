# read instrument data from instr.dat
# data are organized in three vectors: freq, rms (uK/arcmin) and fwhm

import configparser
import numpy as np

def readInstData():

  config = configparser.ConfigParser()
  config.read("instr.ini")

  fwhm = config.get("FWHM","fwhm_list")
  sens = config.get("SENS","sens_list")
  freq = config.get("FREQ","freq_list")
  gain = config.get("GAIN","gain_rms")
  tele = config.get("TELE","tele_list")

  fwhm = (fwhm.split(","))
  sens = (sens.split(","))
  freq = (freq.split(","))
  gain = (gain.split(","))
  tele = (tele.split(","))

  #convert list of str into list of double
  for index, item in enumerate(fwhm):
    fwhm[index] = np.float64(item)

  for index, item in enumerate(sens):
    sens[index] = np.float64(item)

  for index, item in enumerate(freq):
    freq[index] = np.float64(item)

  for index, item  in enumerate(gain):
    gain[index] = np.float64(item)

  return fwhm, sens, freq, gain, tele


def readSkyData():

   config = configparser.ConfigParser()
   config.read("inpData.ini")

   gal_alm_dir = config.get("GALALM","gal_alm_dir")
   gal_alm_basename = config.get("GALALM","gal_alm_basename")

   cmb_dir = config.get("CMB","cmb_dir")
   cmb_spec_r0 = config.get("CMB","cmb_spec_r0")
   cmb_spec_r1 = config.get("CMB","cmb_spec_r1")
   nside = config.get("SIMDATA","nside")

   return gal_alm_dir, gal_alm_basename, cmb_dir, cmb_spec_r0, cmb_spec_r1, nside
