# Social Media Influence Analyzer

This is a project in social media influence analysis using Computer Science to detect and classify influences between users of social media. The project is carried out by Mohammed Z. Guniem to acheive the objective of his master thesis in producing a secure and reliable system for detecting and classifying influences between users on social media platforms.

This repository contains all project code, documents and other related files and folders.

To set up the project on your preffered enviornment, please follow the steps below

---

## I. Importing project source code

Please follow the step below before precessing into setting up any development or production environments

#### I-A. Clone or download the project code of this repository to your favorite location on your machine

- If cloning: Download and install the Git tool using this link https://git-scm.com/downloads
- If downloading directly: unzip the project files in your favorite location

#### I-B. Add necessary environment variables

- Rename the file .env.example to .env
- Fill in the following necessary environment variables

| Variable                    | default value | possible values                                                                                                            |
| --------------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------- |
| COMPOSE_PROJECT_NAME        | smia          | any project name of your choice                                                                                            |
| FLASK_ENV                   | development   | production (for production enviorments)                                                                                    |
|                             |               | development (for testing and development enviorments)                                                                      |
| IS_DOCKER                   | True          | True (if using Docker)                                                                                                     |
|                             |               | False (if not using Docker)                                                                                                |
| reddit_username             | -             | The username of administrating reddit account                                                                              |
| reddit_password             | -             | The password of administrating reddit account                                                                              |
| reddit_client_id            | -             | The client id for crawling reddit                                                                                          |
| reddit_client_secret        | -             | The client secret for crawling reddit                                                                                      |
| reddit_user_agent           | -             | The user agent for crawling reddit                                                                                         |
| mongo_db_version            | 4.4.6         | any compatible version og Mongo DB (remember to test and evaluate before switching to another version)                     |
| mongo_db_host               | 127.0.0.1     | The IP address of the Mongo DB host                                                                                        |
| mongo_db_port               | 27017         | The dedicated port on the Mongo DB host                                                                                    |
| mongo_db_user               | -             | The username of administrating Mongo DB account with full write and read access                                            |
| mongo_db_pass               | -             | The password of administrating Mongo DB account with full write and read access                                            |
| neo4j_users_db_version      | 4.2.5         | any compatible version og Neo4j DB for user graphs (remember to test and evaluate before switching to another version)     |
| neo4j_users_db_host         | 127.0.0.1     | The IP address of the Neo4j DB instance host for user graphs                                                               |
| neo4j_users_http_port       | 7474          | The dedicated http UI port on the Neo4j DB instance host for user graph                                                    |
| neo4j_users_db_port         | 7687          | The dedicated bolt port on the Neo4j DB instance host for user graph                                                       |
| neo4j_users_db_user         | -             | The username of administrating Neo4j DB instance host for user graph with full write and read access                       |
| neo4j_users_db_pass         | -             | The password of administrating Neo4j DB instance host for user graph with full write and read access                       |
| neo4j_activities_db_version | 4.2.5         | any compatible version og Neo4j DB for activity graphs (remember to test and evaluate before switching to another version) |
| neo4j_activities_db_host    | 127.0.0.1     | The IP address of the Neo4j DB instance host for activity graphs                                                           |
| neo4j_activities_http_port  | 7475          | The dedicated http UI port on the Neo4j DB instance host for activity graph                                                |
| neo4j_activities_db_port    | 7688          | The dedicated bolt port on the Neo4j DB instance host for activity graph                                                   |
| neo4j_activities_db_user    | -             | The username of administrating Neo4j DB instance host for activity graphs with full write and read access                  |
| neo4j_activities_db_pass    | -             | The password of administrating Neo4j DB instance host for activity graphs with full write and read access                  |

---

## II. Setting up the development environment (Using Docker)

#### II-A. Download Docker Desktop

- Download and install Docker Desktop using this link https://www.docker.com/products/docker-desktop
- Open Docker Desktop
- Go to Settings -> Resources -> File Sharing
- Share the src in the project directory file by adding its path on your machine to the list

#### II-B. Set up a dockerized development environment

- Open a command line window on you machine as an administrator, preferably git bash
- Navigate to your location in step A above <br />
  `cd {your_location}`
- Now, navigate to your src code folder <br />
  `cd src`
- Spin up all configured containers in the docker-compose.yml file process using attached mode <br />
  `docker-compose up -d`
- Docker will now pull images for mongodb and neo4j and then set up the required services for this project.
- Docker will also build a user-interface image and run this project as a container with Python and its required packages installed.
- This might take a couple of minutes at the first time since pulling images is a little time-consuming
- Please wait for a couple of minutes depending on the capabilities of your system until the mongoDB and neo4j database services are up and running
- Then, go to localhost:5000 or host.docker.internal:5000 on your browser with javascript enabled.
- You should now be able to access the GUI interface of the project.

#### II-C. Importing datasets and generating user and activity graphs, and statistics plots

- In your command line, access smia CLI using the command below or version of it depanding on your command line <br />
  `docker exec -t -i user-interface bash`

#### II-C-1. Importing the small dummy test dataset

- Run test driver <br />
  `python test_driver.py`

Note! You might get a couple of warnings when building the user- and activity user graph, this is because the dummy dataset is very small and there is not enough labels in the training dataset for topic classification. The warnings can be ignored as this is just a dummy dataset for development and testing purposes.

#### II-C-2. Importing a real-life dataset from crawling Reddit

- Run reddit driver <br />
  `python reddit_driver.py`

- exit the CLI <br />
  `exit`

---

## III. Setting up the production environment (User Windows IIS)

Follow the steps below to set up a production envirnoment using Windows IIS:

#### III-A. Install Python

- Download and install Python using from the official python site, https://www.python.org/downloads/
- Åpen a command line on your machine, and install the needed python packages for this project
  `pip install pymongo`
  `pip install neo4j`
  `pip install sklearn`
  `pip install python-dotenv`
  `pip install pandas`
  `pip install praw`
  `pip install matplotlib`
  `pip install flask`

#### III-B. Install MongoDB Archeive Database Server

- Install Mongo DB and create user credentials
- After installation, Open MongoDB Compass and connect to DB
- Extend the commandline below, and create user credentials with your username and password using the follwoing commands
  `use admin`
  `db.createUser({user: "<username>" , pwd: "<password>", roles: [ "userAdminAnyDatabase","readWriteAnyDatabase" ]})`
- Note down the the username and password for later use.
- Open `<Mongo_Installation_Folder>/.../bin/mongod.conf` and enable authentication by adding the following configuration
  `security:`
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`authorization: "disabled"`
- Open PowerShell as admin. and restart the mongodb service using this command
- `Restart-Service -Name "mongodb"`

#### III-C. Install Neo4j User Graph Database Server

- Download and install Neo4j server using this link https://neo4j.com/download-center/#community
- Unzip the downloaded zip folder to `{your_target_locations}/neo4j_users`
- Go to `{your_target_locations}/neo4j_users/neo4j.conf`
- Open as an administrator and change to the following settings configuration to set up the server instance for users
  `# Bolt connector`
  `dbms.connector.bolt.enabled=true`
  `dbms.connector.bolt.tls_level=DISABLED`
  `dbms.connector.bolt.listen_address=:7687`
  `dbms.connector.bolt.advertised_address=:7687`

  `# HTTP Connector. There can be zero or one HTTP connectors.`
  `dbms.connector.http.enabled=true`
  `dbms.connector.http.listen_address=:7474`
  `dbms.connector.http.advertised_address=:7474`

  `# Name of the service`
  `dbms.windows_service_name=neo4j_users`

  `# A comma separated list of procedures and user defined functions that are allowed`
  `# full access to the database through unsupported/insecure internal APIs.`
  `#dbms.security.procedures.unrestricted=my.extensions.example,my.procedures.*`
  `dbms.security.procedures.unrestricted=gds.*`

  `# A comma separated list of procedures to be loaded by default.`
  `# Leaving this unconfigured will load all procedures found.`
  `#dbms.security.procedures.allowlist=apoc.coll.*,apoc.load.*,gds.*`
  `dbms.security.procedures.whitelist=gds.*`

- Open PowerShell or CMD as administrator
- Navigate to your installation folder at path `{your_target_locations}/neo4j_users/bin`
- Set initial passowrd to be "secret" for default username "neo4j"
  `.\neo4j-admin.bat set-initial-password secret --require-password-change`
- Run the following command to install neo4j as a windows service
  `.\neo4j.bat install-service`
- Start the service
  `Start-Service -Name "neo4j_users"`
- Now go to http://localhost:7474/browser/ at your browser, set a password and note it down
- At the end, you can go to http://localhost:7474/browser/ at your browser, set a password and note it down

#### III-B. Install Neo4j Activity Graph Database Server

- Download and install Neo4j server using this link https://neo4j.com/download-center/#community
- Unzip the downloaded zip folder to `{your_target_locations}/neo4j_activities`
- Go to `{your_target_locations}/neo4j_activities/neo4j.conf`
- Open as an administrator and change to the following settings configuration to set up the server instance for activities
  `# Bolt connector`
  `dbms.connector.bolt.enabled=true`
  `dbms.connector.bolt.tls_level=DISABLED`
  `dbms.connector.bolt.listen_address=:7688`
  `dbms.connector.bolt.advertised_address=:7688`

  `# HTTP Connector. There can be zero or one HTTP connectors.`
  `dbms.connector.http.enabled=true`
  `dbms.connector.http.listen_address=:7475`
  `dbms.connector.http.advertised_address=:7475`

  `# Name of the service`
  `dbms.windows_service_name=neo4j_activities`

  `# A comma separated list of procedures and user defined functions that are allowed`
  `# full access to the database through unsupported/insecure internal APIs.`
  `#dbms.security.procedures.unrestricted=my.extensions.example,my.procedures.*`
  `dbms.security.procedures.unrestricted=gds.*`

  `# A comma separated list of procedures to be loaded by default.`
  `# Leaving this unconfigured will load all procedures found.`
  `#dbms.security.procedures.allowlist=apoc.coll.*,apoc.load.*,gds.*`
  `dbms.security.procedures.whitelist=gds.*`

- Open PowerShell or CMD as administrator
- Navigate to your installation folder at path `{your_target_locations}/neo4j_activities/bin`
- Set initial passowrd to be "secret" for default username "neo4j"
  `.\neo4j-admin.bat set-initial-password secret --require-password-change`
- Run the following command to install neo4j as a windows service
  `.\neo4j.bat install-service`
- Start the service
  `Start-Service -Name "neo4j_activities"`
- Now go to http://localhost:7475/browser/ at your browser, set a password and note it down
- At the end, you can go to http://localhost:7475/browser/ at your browser, set a password and note it down

#### III-D. Install User Interface Web Server using IIS.
