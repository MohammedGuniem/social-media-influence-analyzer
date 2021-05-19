# Master Thesis Project
 
### Install Python
https://www.python.org/downloads/

### Install Mongo DB and create user credentials
https://www.mongodb.com/try/download/community

- After installation, Open MongoDB Compass and connect to DB

- Extend the commandline below, and create user credentials with your username and password using the follwoing commands

use admin

db.createUser({user: "<username>" , pwd: "<password>", roles: [  "userAdminAnyDatabase","readWriteAnyDatabase" ]})

Note down the the username and password for later use.

Open <Mongo_Installation_Folder>/.../bin/mongod.conf and enable authentication by adding the following configuration

security:
    authorization: "disabled"

Open PowerShell as admin. and restart the mongodb service using this command

Restart-Service -Name "mongodb"

### Install 2 Neo4j server instances and set user credentials
https://neo4j.com/download-center/#community

- You need to unzip the downloaded zip folder 2 times, one for each neo4j server instance

### Setting up the users server instance
- unzip content to your <target_locations>
<target_locations>/neo4j_users
<target_locations>/neo4j_activities

- Go to 
<target_locations>/neo4j_users/neo4j.conf

- Open as an administrator and change to the following settings configuration to set up the server instance for users
# Bolt connector
dbms.connector.bolt.enabled=true
dbms.connector.bolt.tls_level=DISABLED
dbms.connector.bolt.listen_address=:7687
dbms.connector.bolt.advertised_address=:7687

# HTTP Connector. There can be zero or one HTTP connectors.
dbms.connector.http.enabled=true
dbms.connector.http.listen_address=:7474
dbms.connector.http.advertised_address=:7474

# Name of the service
dbms.windows_service_name=neo4j_users

# A comma separated list of procedures and user defined functions that are allowed
# full access to the database through unsupported/insecure internal APIs.
#dbms.security.procedures.unrestricted=my.extensions.example,my.procedures.*
dbms.security.procedures.unrestricted=gds.*

# A comma separated list of procedures to be loaded by default.
# Leaving this unconfigured will load all procedures found.
#dbms.security.procedures.allowlist=apoc.coll.*,apoc.load.*,gds.*
dbms.security.procedures.whitelist=gds.*

- Open PowerShell or CMD as administrator
- Navigate to your installation folder at path "<target_locations>/neo4j_users/bin"

- Set initial passowrd to be "secret" for default username "neo4j"
.\neo4j-admin.bat set-initial-password secret --require-password-change

- Run the following command to install neo4j as a windows service
.\neo4j.bat install-service

- Start the service
Start-Service -Name "neo4j_users"

- Now go to http://localhost:7474/browser/ at your browser, set a password and note it down


### Setting up the activities server instance
- Repeat the same steps above, but using the neo4j_activitites installation folder and the following configuration in <target_locations>/neo4j_activities/neo4j.conf

# Bolt connector
dbms.connector.bolt.enabled=true
dbms.connector.bolt.tls_level=DISABLED
dbms.connector.bolt.listen_address=:7688
dbms.connector.bolt.advertised_address=:7688

# HTTP Connector. There can be zero or one HTTP connectors.
dbms.connector.http.enabled=true
dbms.connector.http.listen_address=:7475
dbms.connector.http.advertised_address=:7475

# A comma separated list of procedures and user defined functions that are allowed
# full access to the database through unsupported/insecure internal APIs.
#dbms.security.procedures.unrestricted=my.extensions.example,my.procedures.*
dbms.security.procedures.unrestricted=gds.*

# A comma separated list of procedures to be loaded by default.
# Leaving this unconfigured will load all procedures found.
#dbms.security.procedures.allowlist=apoc.coll.*,apoc.load.*,gds.*
dbms.security.procedures.whitelist=gds.*

# Name of the service
dbms.windows_service_name=neo4j_activities

- Start the service
Start-Service -Name "neo4j_activities"

- At the end, you can go to http://localhost:7475/browser/ at your browser, set a password and note it down

### Install Neo4j Graph Data Science
- https://neo4j.com/download-center/#community

extract in the plugin folder in you neo4j installation folder

### Install Python libraries
pip install pymongo
pip install neo4j
pip install sklearn
pip install python-dotenv
pip install pandas
pip install praw
pip install matplotlib
pip install flask

### copy project code over
...

### Edit. Env file
...

### Create Reddit analyzer user
https://www.youtube.com/watch?v=gIZJQmX-55U

### Run test round locally
python test_driver.py
python reddit_driver.py
python remove_old_graphs.py

### Schedule a routine crawling process
If you want to crawl a certain network periodically in time, you can set a job for this on your server
If using Windows, you might want to use the capabilities of Task Scheduale to accomplish this.

### Publish the UI Webserver
The user interface can be published as a public webserver within a certain network or across the Internet
You may use a server technology of your choice, If you are using Windows then you might want to use the capabilities of IIS to publish.

### Using a Cloud Service
It is also possible to use a Cloud Service to accomplish this instead of an on-premises setup.
Refer to the documentation of you Cloud Provider for details on how to set up periodic task and Flask webserver written in Python. 

### Using Docker
Install: Docker Desktop
Run: docker-compose up
Install: Python
Navigate to you project directory
Run: pip install -r requirements
Run: python test_driver.py
Run: python reddit_driver.py
Run: python ui_web_server.py