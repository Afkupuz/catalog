# catalog
Udacity project 3

Configuration:<br>
In this project I developed an internal server that serves localhost port 5000
updated virtual machine with:
pip install werkzeug==0.8.3
pip install flask==0.9

Project details
Using Flask, CRUD, and SQLAlchemy I have prepared a web application that allows users to log in via google and facebook using oauth2.
Templates are presented depending on URL requests and serve infromation stored in the sql database.

Features
This site provides users with the ability to create subjects and respond to other peoples subjects.
Users can edit and delete their subjects as well as censor posts they dont like, but they can't touch other peoples subjects
Users can delete their own responses, but can not interact with other peoples sujects or responses.
The sidebar is updated with recent posts and the header provides navigation control.
JavaScript confirms before deleting, and prevents people from posting blank posts. These buttons still work if javascript is turned off.
There is also built-in seurity in that the server checks user ids against the current session to prevent direct url access and session hijacking.

Operation
Populate.py fills in some basic database information with two users and some subjects and responses.
Start the server using project.py and open your browser to localhost:5000/
