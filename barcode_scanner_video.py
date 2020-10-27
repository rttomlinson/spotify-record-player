# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
#import argparse
import datetime
import imutils
import time
import cv2
import requests
#import sqlite3
import subprocess
import base64
import os
import json
from dotenv import load_dotenv
load_dotenv()

# construct the argument parser and parse the arguments
#ap = argparse.ArgumentParser()

def use_refresh_token_for_new_access_token(access_credentials):
    # Get new access token
    url = "https://accounts.spotify.com/api/token"
    b64encoded_data = base64.b64encode((access_credentials["client_id"] + ":" + access_credentials["client_secret"]).encode("utf-8")).decode("utf-8")
    headers = {"Authorization": "Basic " + b64encoded_data}
    r = requests.post(url, headers=headers, data={"grant_type": "refresh_token", "refresh_token": access_credentials["refresh_token"]})

    token_data = r.json()

    # Return the access token
    return token_data["access_token"]

# Check if this fails
def get_playback_status(access_token, headers):
    #access_token = use_refresh_token_for_new_access_token(access_credentials)
    url = "https://api.spotify.com/v1/me/player"
    #headers = {"Authorization": "Bearer " + access_token}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        println("Status code from playback status endpoint is " + r.status_code)
        return False
    payload = r.json()
    return payload

def get_playback_status_with_retry():
    get_playback_status()
# Playback status payload example
"""
{
  "timestamp": 1490252122574,
  "device": {
    "id": "3f228e06c8562e2f439e22932da6c3231715ed53",
    "is_active": false,
    "is_restricted": false,
    "name": "Xperia Z5 Compact",
    "type": "Smartphone",
    "volume_percent": 54
  },
  "progress_ms": "44272",
  "is_playing": true,
  "currently_playing_type": "track",
  "actions": {
    "disallows": {
      "resuming": true
    }
  },
  "item": {},
  "shuffle_state": false,
  "repeat_state": "off",
  "context": {
    "external_urls" : {
      "spotify" : "http://open.spotify.com/user/spotify/playlist/49znshcYJROspEqBoHg3Sv"
    },
    "href" : "https://api.spotify.com/v1/users/spotify/playlists/49znshcYJROspEqBoHg3Sv",
    "type" : "playlist",
    "uri" : "spotify:user:spotify:playlist:49znshcYJROspEqBoHg3Sv"
  }
}
"""
##########
# Basically we want these to keep polling the playback status until it reports that the state has changed.
def transfer_playback():
    pass

def turn_off_shuffle():
    pass

def change_album():
    pass


def make_song_request(access_credentials, uri):
    access_token = use_refresh_token_for_new_access_token(access_credentials)
    # Restart the raspotify daemon
    # This kicks anyone on raspotify off and resets our account on the device 
    # There's probably a better way to do this with librespot directly
    subprocess.run(["sudo", "systemctl", "restart", "raspotify"])
    # wait to give the daemon time to restart
    time.sleep(2.0)

    headers = {"Authorization": "Bearer " + access_token}
    
    # Always cast to device raspberry pi device (This will kick whoever is on off)
    # TODO figure out how to manage this device id
    raspotify_device_id = access_credentials["device_id"]
    # How to get device id? Does it change or always the same??
    
    # Get current status of playback
    
    playback_current_status = get_playback_status(access_token, headers)
    api_request_failure_threshold = 0
    while ((not playback_current_status) and (api_request_failure_threshold < 10)):
        api_request_failure_threshold += 1
        time.sleep(0.1)
        playback_current_status = get_playback_status(access_token, headers)
        

    # Do we care about retry? 
    r_transfer_playback = requests.put("https://api.spotify.com/v1/me/player", headers=headers, json={"device_ids":[raspotify_device_id], "play": True})
    # Wait for state?
    
    # has playback been transfered to specified device?
    
    # Do we care about retry?
    # Always turn shuffle off
    r_shuffle = requests.put("https://api.spotify.com/v1/me/player/shuffle?state=false", headers=headers)
    # Wait for state?

    # is playback status shuffle off?

    # Do we care about retry?
    # Change the album
    r = requests.put("https://api.spotify.com/v1/me/player/play", headers=headers, json={"context_uri":uri})
    # Wait for state?

    # based on regex is it a uri or url?
    # based on this, change the location to look for the value

    # What about youtube? It's a completely different path

    # assuming everything worked. set current album to uri
    return {"current_album": uri, "frames_with_no_input": 0}


###############

def pause_playback(access_credentials):
    pause_url = "https://api.spotify.com/v1/me/player/pause"
    access_token = use_refresh_token_for_new_access_token(access_credentials)

    headers = {"Authorization": "Bearer " + access_token}
    r = requests.put(pause_url, headers=headers)
    # Wait for state?
    return {"current_album": None, "frames_with_no_input": 0}

def start_video_stream(access_credentials, frames_pause_threshold = 6, time_between_scans = 0.1):        
    
    scanner_state = {"current_album": None, "frames_with_no_input": 0}
    
    # Add "frames tracking for detecting how many frames of no-input
    
    # initialize the video stream and allow the camera sensor to warm up
    print("[INFO] Starting the video stream...")

    vs = VideoStream(usePiCamera=True).start()
    print("video should be streaming")
    time.sleep(2.0)

    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it to have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        # find the barcodes in the frame and dcode each of the barcodes
        barcodes = pyzbar.decode(frame)

        # If nothing playing and no album, do nothing
        if len(barcodes) == 0:
            # if current_album set to None and stop playing track
            if scanner_state["current_album"] != None:
                if scanner_state["frames_with_no_input"] > frames_pause_threshold:
                    # Should we "wait" until playback is paused before proceeding?
                    # We could consider adding a timeout for these operations?
                    # Should probably do that in general for hitting external APIs
                    scanner_state = pause_playback(access_credentials)
                else:
                    # Would rather return a new dictionary, but I'm not confident in python garbage collection
                    scanner_state["frames_with_no_input"] = scanner_state["frames_with_no_input"] + 1

        # loop over the detected barcodes
        for barcode in barcodes:
            # the barcode data is a bytes object
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

            if barcodeData != scanner_state["current_album"]:
                scanner_state = make_song_request(access_credentials, barcodeData)
            
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key was pressed, break from the loop
        if key == ord("q"):
            break
        
        # Sleep here so we aren't spamming. Or wait for keyboard input
        time.sleep(time_between_scans)
    # close the output CSV and clean-up
    print("[INFO] cleaning up...")
    cv2.destroyAllWindows()
    vs.stop()

if __name__ == "__main__":

    try:
        #args = vars(ap.parse_args())
        data_file_path = os.getenv("DATA_FILE")
        with open(data_file_path) as in_file:
            access_credentials = json.load(in_file)
            start_video_stream(access_credentials)
        # Or do something else, doesn't really matter for this app. Fetch from a secrets manager

    finally:
        # We can also close the connection if we are done with it
        # Just  be sure any changes have been committed or they will be lost
        # conn.close()
        # access_credential data should not change during operation
        pass

