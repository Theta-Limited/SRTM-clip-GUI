#!/usr/bin/env python3
# fetchdem.py
# Bobby Krupczak
# Theta Limited
# rdk@theta.limited
# 
# fetch digital elevation models/maps (DEMs) from OpenTopography using their web API
# write into a GeoTIFF file for use with OpenAthena applications
# Users need an API key to use this script; free from OpenTopography
# provide either through environment variable or via command-line
#
# To obtain an OpenTopography API Key, go to https://opentopography.com
# and create an account then request API KEY.

import os
import sys
import getopt
import argparse
import math
import requests

lat = 0.0
lon = 0.0
n = 0.0
s = 0.0
w = 0.0
e = 0.0
diam = 15000
apiKeyStr = ""
urlStr = "https://portal.opentopography.org/API/globaldem?"
demTypeStr = "SRTMGL1"
outputFormatStr = "GTiff"
requestURLStr = ""
verbose = False

# -------------------------------
# given lat, lon of center, get bounding box 

def getBoundingBox():

    global n,s,e,w,diam

    if verbose:
       print("Center is ",lat,",",lon)
    
    clat = lat * (math.pi / 180.0)
    clon = lon * (math.pi / 180.0)
    d = math.sqrt( 2.0 * (diam / 2.0) * (diam / 2.0) )

    # go southwest X meters
    # SW = 225 degrees
    bearing = 225.0 * (math.pi / 180.0)
    arcLen = d / (6371 * 1000)

    if verbose:
       print("getBoundingBox: diam is ",diam," d is ",d," arcLen is ",arcLen)    

    newLat = math.asin(math.sin(clat) * math.cos(arcLen) + math.cos(clat) * math.sin(arcLen) * math.cos(bearing) )
    newLon = clon + math.atan2(math.sin(bearing) * math.sin(arcLen) * math.cos(clat), math.cos(arcLen) - math.sin(clat) * math.sin(newLat))
    llLat = newLat * (180.0 / math.pi)
    llLon = newLon * (180.0 / math.pi)
        
    # go northeast X meters
    # NE = 45
    bearing = 45.0 * (math.pi / 180.0)
    newLat = math.asin(math.sin(clat) * math.cos(arcLen) + math.cos(clat) * math.sin(arcLen) * math.cos(bearing) )
    newLon = clon + math.atan2(math.sin(bearing) * math.sin(arcLen) * math.cos(clat), math.cos(arcLen) - math.sin(clat) * math.sin(newLat))
    urLat = newLat * (180.0 / math.pi)
    urLon = newLon * (180.0 / math.pi)

    # truncate to 6 decimal places XXX
    s = truncate(llLat,6)
    w = truncate(llLon,6)
    n = truncate(urLat,6)
    e = truncate(urLon,6)

    if verbose:
       print("Bounding box: ",s,w,n,e)

    return
    
# -------------------------------

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 **n

# -------------------------------
# main

# try to get API key from environment variable
apiKeyStr = os.getenv("OPENTOPOGRAPHY_API_KEY","")

if apiKeyStr != "" and verbose:
     print("Read OPENTOPOGRAPHY_API_KEY from environment")

parser = argparse.ArgumentParser()
parser.add_argument("-v",action="store_true",default=False,help="verbose output")
parser.add_argument("-lat",type=float,help="center latitude in decimal format",default=0.0)
parser.add_argument("-lon",type=float,help="center longitutde in decimal format",default=0.0)
parser.add_argument("-diam",type=int,help="length of side of bounding box in meters",default=0)
parser.add_argument("-apikey",help="OpenTopography API key either; either set env var OPENTOPOGRAPHY_API_KEY or provide via command-line arg",default="")
args = parser.parse_args()

# if no API key, exit
verbose = args.v
lat = args.lat
lon = args.lon
if lat == 0.0 or lon == 0.0:
   parser.error("You must specify a lat and lon")

if args.diam == 0:
   parser.error("You must specify a bounding box length")

if args.apikey != "":
   apiKeyStr = args.apikey

if apiKeyStr == "" or apiKeyStr == "INeedAnApiKey":
   parser.error("You need an API key to download DEMs from OpenTopography")

# compute bounding box; results in global variables n,s,e,w
getBoundingBox()

requestURLStr = urlStr + "demtype=" + demTypeStr + "&south=" + str(s) + "&north=" + str(n) + "&west=" + str(w) + "&east=" + str(e) + "&outputFormat=" + outputFormatStr + "&API_Key=" + apiKeyStr

if verbose:
   print("Request URL is ",requestURLStr)

# make the request and write file to DEM_LatLon_s_w_n_e.tiff
response = requests.get(requestURLStr)

if verbose:
    print("Response status code is ",response.status_code)

if response.status_code == 200:
    if verbose:
       print("Response contains ",len(response.content)," bytes")
	
    filename = "DEM_LatLon_"+str(s)+"_"+str(w)+"_"+str(n)+"_"+str(e)+".tiff"

    if verbose:
       print("Writing response to ",filename)

    print("Wrote ",len(response.content)," to ",filename)

    f = open(filename,"wb+")
    f.write(response.content)
    f.close()
    
else:
    match response.status_code:
      case 400:
         print("Bad request: bug in code perhaps?")
      case 401:
         print("Unauthorized: check your API key:",apiKeyStr)
      case 403:
         print("Forbidden: check your API key:",apiKeyStr)
      case 404:
         print("Not found: check the URL to see if API changed")
      case 408:
         print("Request timeout: are you connected to the InterWebs?")
      case _:
         print("Failed to fetch DEM, error code is:",response.status_code)

