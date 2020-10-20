uses sqlite3
We just need some kind of remote data store. We could actually just use a file.And is completely reasonable since the data should never change.
you can also put the data in a database if you want a little exposure to sql databases. I have the code commented out if you want to do that
But this is fine exposure to a simple database :) and super easy to use and install
* sudo apt-get install sqlite3

https://github.com/spotify/web-api-auth-examples

Environment variables:
DATA_FILE - file path to json data
requires
client_id
client_secret
device_id
access_token
refresh_token

can use the python .env library

Steps to deploy:

Get the device ID. I believe the device ID is assigned to a device based on maybe a MAC address from Spotify? I'm not sure how Spotify does it but the device ID does not appear to change. 

you also need a dedicated spotify account since we reinitize the raspotify/librespot utility each time we change songs to register the device with spotify.

Initialization can also happen by fetching the device ID based on device name which you also set.

you need to acquire an access token and refresh token using the authorization grant
