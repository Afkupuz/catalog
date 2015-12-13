# catalog
Udacity project 3

In this project I developed my own internal server that serves localhost on port 8000

Using Flask, CRUD, and SQLAlchemy I have prepared a web application that allows users to log in via google and facebook using oauth2.

Templates are presented depending on URL requests and serve infromation stored in the sql database.

This site provides users with the ability to create subjects and respond to other peoples subjects.

Users can edit and delete their subjects as well as censor posts they dont like, but they can't touch other peoples subjects

Users can delete their own responses, but can not interact with other peoples sujects or responses.

The sidebar is updated with recent posts and the header provides navigation control.

JavaScript confirms before deleting, and prevents people from posting blank posts. These buttons still work if javascript is turned off.

There is also built-in seurity in that the server checks user ids against the current session to prevent direct url access and session hijacking.

Populate.py fills in some basic database information with two users and some subjects and responses.
