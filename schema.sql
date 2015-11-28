DROP TABLE if EXISTS user;

CREATE TABLE user (
id integer PRIMARY KEY autoincrement,
username text NOT NULL,
password text NOT NULL
);

DROP TABLE if EXISTS post;

CREATE TABLE post (
id integer PRIMARY KEY autoincrement,
Uid text NOT NULL,
title text NOT NULL,
post text NOT NULL,
loc text NOT NULL
);

