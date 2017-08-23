-- Database: sbux

-- DROP DATABASE sbux;

CREATE DATABASE sbux
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

CREATE TABLE tweets (
	message text,
    created_at timestamp,
    geo text,
    src text
)

CREATE FUNCTION notify_trigger() RETURNS trigger AS $$
DECLARE
BEGIN
    PERFORM pg_notify('tweets', NEW.message);
    RETURN new;
END;
$$ LANGUAGE plpgsql

CREATE TRIGGER sbux_tweets_trigger AFTER INSERT ON tweets
FOR EACH ROW EXECUTE PROCEDURE notify_trigger();