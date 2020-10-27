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
    c.execute("""SELECT * FROM users WHERE id=1""")
    # Should return a tuple in the form (id, access_token, refresh_token)
    data = c.fetchone()
    refresh_token = data[2] # refresh_token in position 2

    # Get new access token
    url = "https://accounts.spotify.com/api/token"
    b64encoded_data = base64.b64encode((access_credentials["client_id"] + ":" + access_credentials["client_secret"]).encode("utf-8")).decode("utf-8")
    headers = {"Authorization": "Basic " + b64encoded_data}
    r = requests.post(url, headers=headers, data={"grant_type": "refresh_token", "refresh_token": access_credentials["refresh_token"]})

    token_data = r.json()

    # Update the table if you want to fetch from the table
    c.execute("""UPDATE users SET access_token = ? WHERE id=1""", [token_data["access_token"]])
    conn.commit()

    # Return the access token
    return token_data["access_token"]

