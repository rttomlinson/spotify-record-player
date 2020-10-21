Environment variables:
DATA_FILE - file path to json data

You need to update the /etc/default/raspotify file to use. This values are simply passed to the librespot
Optionally: 
DEVICE_NAME="raspotify" (How the device shows up in the menu)
Required:
OPTIONS="--username <spotify_username> --password <spotify_password>"

username and password should be for a dedicated spotify account and not used in ANY of your other accounts. The reason for this is that this data is stored in plaintext and one should not rely on raspberry pi default settings for securely storing data on the device. If someone wants to implement some kind of secret store for these values then go for it. 

requires in json
client_id: string
client_secret: string
device_id: string
access_token: not actually required (could be optimized)
refresh_token: string

can use the python .env library

Steps to deploy:

Get the device ID. I believe the device ID is assigned to a device based on maybe a MAC address from Spotify? I'm not sure how Spotify does it but the device ID does not appear to change. 

you also need a dedicated spotify account since we reinitize the raspotify/librespot utility each time we change songs to register the device with spotify.

Initialization can also happen by fetching the device ID based on device name which you also set.

you need to acquire an access token and refresh token using the authorization grant
https://github.com/spotify/web-api-auth-examples

uses sqlite3
We just need some kind of remote data store. We could actually just use a file.And is completely reasonable since the data should never change.
you can also put the data in a database if you want a little exposure to sql databases. I have the code commented out if you want to do that
But this is fine exposure to a simple database :) and super easy to use and install
* sudo apt-get install sqlite3

