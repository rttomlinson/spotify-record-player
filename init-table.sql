CREATE TABLE users (id integer primary key, access_token text, refresh_token text, device_id text, client_id text, client_secret text);
INSERT INTO users (access_token, refresh_token) VALUES ("111", "aaa", "hello", "client_id", "client_secret"); -- initialize the table with real values
