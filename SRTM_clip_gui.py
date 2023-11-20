#!/usr/bin/env python3
# SRTM_clip_gui.py
# Matthew Krupczak, Bobby Krupczak
# Theta Limited

import PySimpleGUI as sg
import sys
import os
import math
import requests
import getopt

lat = 0.0
lon = 0.0
n = 0.0
s = 0.0
w = 0.0
e = 0.0
diam = 15000

# to build a binary using pyinstaller, hardcode apiKeyStr
apiKeyStr = "d9fe991567394da8d9573bd3e1571f22"

urlStr = "https://portal.opentopography.org/API/globaldem?"
demTypeStr = "SRTMGL1"
outputFormatStr = "GTiff"
filenameSuffix = ".tiff"
requestURLStr = ""
verbose = False
application_path = ""

# TODO: get separate API key, hard code, and then compile/build
# windows/x86 app binary, mac/m1 binary, mac/x86 binary, and linux
# x86 binary.
# take out API key field from GUI and hardcode for the pre-compiled
# versions, then put it back in for source code python git submission

# DEMs generated from this program successfully tested with
# OA/python, OAiOS, OAandroid

# -------------------------------
# given lat, lon of center, get bounding box 

def getBoundingBox():

    global n,s,e,w,diam
    
    clat = lat * (math.pi / 180.0)
    clon = lon * (math.pi / 180.0)
    d = math.sqrt( 2.0 * (diam / 2.0) * (diam / 2.0) )

    if verbose:
       print("Center lat,lon is ",clat,clon," within ",diam," x ",diam," box")

    # go southwest X meters
    # SW = 225 degrees
    bearing = 225.0 * (math.pi / 180.0)
    arcLen = d / (6371 * 1000)

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
       print("Bounding box is ",s,w,n,e)

    return
    
# -------------------------------

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 **n

def textToInt(t):
    try:
       value = int(t)
       return value
    except:
       return math.inf

def textToFloat(t):
    try:
       value = float(t)
       return value
    except:
       return math.inf
   
# -------------------------------

def fetchDem():

    global lat, lon, diam, apiKeyStr, window

    # get params out of GUI and sanity check
    window['Results'].update("Going to fetch DEM")

    latText = values['lat']
    lonText = values['lon']
    diamText = values['diam']

    # when building an executable using pyinstaller, don't set apikeystr here
    # apiKeyStr = values['apiKey']

    if latText == '' or lonText == '' or diamText == '' or apiKeyStr == '':
        window['Results'].update("Invalid parameters")
        return

    lat = textToFloat(latText)
    lon = textToFloat(lonText)
    diam = textToInt(diamText)

    if lat == math.inf or lon == math.inf or diam == math.inf:
        window['Results'].update("Invalid parameters")
        return

    # get bounding box
    getBoundingBox()

    # make request
    requestURLStr = urlStr + "demtype=" + demTypeStr + "&south=" + str(s) + "&north=" + str(n) + "&west=" + str(w) + "&east=" + str(e) + "&outputFormat=" + outputFormatStr + "&API_Key=" + apiKeyStr

    
    aStr = "Fetching DEM for "+str(lat)+","+str(lon)+" x "+str(diam)+" meters . . ."
    window['Results'].update(aStr)
    window.refresh()

    if verbose:
       print("Request URL is ",requestURLStr)
    
    # make the request and write file to DEM_LatLon_s_w_n_e.tiff
    response = requests.get(requestURLStr)

    if response.status_code == 200:

       # normally files written to directory with .py script
       # for windows pyinstaller version, we need to
       # set the directory explicitly
        
       filename = "DEM_LatLon_"+str(s)+"_"+str(w)+"_"+str(n)+"_"+str(e)+filenameSuffix
       app_filename = os.path.join(application_path,filename)

       f = open(app_filename,"wb+")
       f.write(response.content)
       f.close()

       aStr = "Wrote " + str(len(response.content)) + " bytes to " + filename
       window['Results'].update(aStr)
       window.refresh()

       if verbose:
          print(aStr)
       
    else:
       if verbose:
          print("Request failed, error code ",response.status_code)

       # no match statement prior to 3.10 and pyinstaller 4.x for windows
       # doesnt support match; so revert back to ifelse
#       match response.status_code:
#         case 204:
#            window['Results'].update("No elevation data for this lat,lon; try again after updating lat,lon")
#         case 400:
#            window['Results'].update("Bad request: bug in code perhaps?")
#         case 401:
#            aStr = "Unauthorized: check your API key:" + apiKeyStr
#            window['Results'].update(aStr)
#         case 403:
#            aStr = "Forbidden: check your API key:" + apiKeyStr
#            window['Results'].update(aStr)
#         case 404:
#            window['Results'].update("Not found: check the URL to see if API changed")
#         case 408:
#            window['Results'].update("Request timeout: are you connected to the InterWebs?")
#         case _:
#            aStr = "Failed to fetch DEM, error code is:" + str(response.status_code)
#            window['Results'].update(aStr)

       rcode = response.status_code
       if rcode == 204:
            window['Results'].update("No elevation data for this lat,lon; try again after updating lat,lon")
       elif rcode == 400:
            window['Results'].update("Bad request: bug in code perhaps?")
       elif rcode == 401:
#           aStr = "Unauthorized: check your API key:" + apiKeyStr
            aStr = "Unauthorized: check your API key"
            window['Results'].update(aStr)
       elif rcode == 403:
            aStr = "Forbidden: check your API key: XXX"
            window['Results'].update(aStr)
       elif rcode == 404:
            window['Results'].update("Not found: check the URL to see if API changed")
       elif rcode == 408:
            window['Results'].update("Request timeout: are you connected to the InterWebs?")	   
       else:
            aStr = "Failed to fetch DEM, error code is:" + str(response.status_code)
            window['Results'].update(aStr)
	       
    # update results with error code or
    # number of bytes written to filename
    # window['Results'].update("Finished, result is X")

    return

# -------------------------------

def usage():
    print(sys.argv[0]," [-v] [-h]")
    sys.exit(0)

# -------------------------------
# main
# check if -v flag set for verbose 

opts, args = getopt.getopt(sys.argv[1:],"vh")
for o, v in opts:
    if o == "-v":
       verbose = True
    if o == "-h":
       usage()
       
if hasattr(sys, '_MEIPASS'):
    # PyInstaller >= 1.6
    os.chdir(sys._MEIPASS)
    os.environ["PATH"] += os.path.sep + sys._MEIPASS
elif '_MEIPASS2' in os.environ:
    # PyInstaller < 1.6 (tested on 1.5 only)
    os.chdir(os.environ['_MEIPASS2'])
    os.environ["PATH"] += os.path.sep + os.environ['_MEIPASS2']
else:
    pass

if getattr(sys,'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)


# try to get API key from environment variable
# when building an executable using pyinstaller, don't pull apikey
# from environment var

# apiKeyStr = os.getenv("OPENTOPOGRAPHY_API_KEY","")

font=(sg.DEFAULT_FONT, 16)

layout = [

    # when building an executable using pyinstaller, don't show the api key
#    [sg.Text('API Key:', font=font), sg.InputText(apiKeyStr, font=font, key='apiKey', tooltip='Register to get your free OpenTopography API key from https://portal.opentopography.org\nPut that API key here or in OPENTOPOGRAPHY_API_KEY environment variable.')],

    [sg.Text('Center Latitude:', font=font), sg.InputText(' 0.0', font=font, key='lat', tooltip='Latitude in decimal format')],
    [sg.Text('Center Longitude:', font=font), sg.InputText(' 0.0', font=font, key='lon', tooltip='Longitude in decimal format')],
    [sg.Text('Height/width (m):', font=font), sg.InputText(' 15000', font=font, key='diam', tooltip='Height/width of the surrounding bounding box in meters.')],
    [sg.Text('Results: Output file will be DEM_LatLon_xxx', font=font, key='Results')],
    [sg.Button('Fetch', font=font)]
]

window = sg.Window('Fetch Digital Elevation Map from OpenTopography', layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == 'Fetch':
        fetchDem()

window.close()
