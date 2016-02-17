# Catalog
The third project as part of Udacity's Full Stack NanoDegree program

##Configuration:<br>
In this project I developed an internal server that serves localhost port 5000<br>
updated virtual machine with:<br>
pip install werkzeug==0.8.3<br>
pip install flask==0.9<br>

##Project details:<br>
Using Flask, REST, CRUD, API endpoints and SQLAlchemy I have prepared a web application that allows users to log in via google and facebook using oauth2.<br>
Templates are presented depending on URL requests and serve infromation stored in the sql database.<br>

1. Install Vagrant and VirtualBox  
2. Clone the fullstack-nanodegree-vm  
3. Launch the Vagrant VM (vagrant up)  
4. Write your Flask application locally in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM).  
5. Run your application within the VM (python /vagrant/catalog/application.py)  
6. Access and test your application by visiting http://localhost:8000 locally  

##My Project:  

To run:  
Have vagrant installed and launch an instance where the tournament folder is accessable  
Example from the OSX terminal:  
$ vagrant up (launches the vagrant server)  
$ vagrant ssh (ssh login to that server)  
$ cd /vagrant/catalog  
  
Populate.py fills in some basic database information with two users and some subjects and responses.<br>
From the catalog folder $ python project.py will host the website on localhost:5000  
  
##Features:<br>
This site provides users with the ability to create subjects and respond to other peoples subjects.<br>
Users can edit and delete their subjects as well as censor posts they dont like, but they can't touch other peoples subjects.<br>
Users can delete their own responses, but can not interact with other peoples sujects or responses.<br>
The sidebar is updated with recent posts and the header provides navigation control.<br>
JavaScript confirms before deleting, and prevents people from posting blank posts. These buttons still work if javascript is turned off.<br>
There is also built-in seurity in that the server checks user ids against the current session to prevent direct url access and session hijacking.<br>

