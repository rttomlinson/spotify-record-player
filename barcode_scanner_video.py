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

# Connect to databse
#basepath = "/home/pi/"
#db_filename = "example.db"
#conn = sqlite3.connect(basepath + db_filename)
#c = conn.cursor()

#def get_access_token():
    # We always assume that id = 1 is the only user and it gets reset each time. Would be cool to do some IOT stuff here.
    #c.execute("""SELECT * FROM users WHERE id=1""")
    # Should return a tuple in the form (id, access_token, refresh_token)
    # data = c.fetchone()
    # return data[1]

def use_refresh_token_for_new_access_token(access_credentials):
    ### sqlite3 code
    # Get refresh token
    # We always assume that id = 1 is the only user and it gets reset each time. Would be cool to do some IOT stuff here.
    #c.execute("""SELECT * FROM users WHERE id=1""")
    # Should return a tuple in the form (id, access_token, refresh_token)
    #data = c.fetchone()
    #refresh_token = data[2] # refresh_token in position 2
    
    # Get new access token
    url = "https://accounts.spotify.com/api/token"
    b64encoded_data = base64.b64encode((access_credentials["client_id"] + ":" + access_credentials["client_secret"]).encode("utf-8")).decode("utf-8")
    headers = {"Authorization": "Basic " + b64encoded_data}
    r = requests.post(url, headers=headers, data={"grant_type": "refresh_token", "refresh_token": access_credentials["refresh_token"]})

    token_data = r.json()

    # Update the table if you want to fetch from the table
    # c.execute("""UPDATE users SET access_token = ? WHERE id=1""", [token_data["access_token"]])
    # conn.commit()

    # Return the access token
    return token_data["access_token"]

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
    r_transfer_playback = requests.put("https://api.spotify.com/v1/me/player", headers=headers, json={"device_ids":[raspotify_device_id], "play": False})
    # Always turn shuffle off
    r_shuffle = requests.put("https://api.spotify.com/v1/me/player/shuffle?state=false", headers=headers)
    
    # Change the album
    baseurl = "https://api.spotify.com/v1/me/player/play"
    r = requests.put(baseurl, headers=headers, json={"context_uri":uri})
    # assuming everything worked. set current album to uri
    return {"current_album": uri, "frames_with_no_input": 0}


def pause_playback(access_credentials):
    pause_url = "https://api.spotify.com/v1/me/player/pause"
    access_token = use_refresh_token_for_new_access_token(access_credentials)

    headers = {"Authorization": "Bearer " + access_token}
    r = requests.put(pause_url, headers=headers)
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

