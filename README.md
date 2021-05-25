# Social Media Influence Analyzer

This is a project in social media influence analysis using Computer Science to detect and classify influences between users of social media. The project is carried out by Mohammed Z. Guniem to acheive the objective of his master thesis in producing a secure and reliable system for detecting and classifying influences between users on social media platforms.

This repository contains all project code, documents and other related files and folders.

To set up the project on your preffered enviornment, please follow the steps below

## I. Setting up the development environment

The development of this project is mainly based on Docker Technology, follow the steps below to set up an environment for development and testing purposes.

#### I-A. Clone or download the project code of this repository to your favorite location on your machine

- If cloning: Download and install the Git tool using this link https://git-scm.com/downloads
- If downloading directly: unzip the project files in your favorite location

#### I-B.

- Fill in the following necessary environment variables before preceeding to the next steps

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

#### I-C. Download Docker Desktop

- Download and install Docker Desktop using this link https://www.docker.com/products/docker-desktop
- Open Docker Desktop
- Go to Settings -> Resources -> File Sharing
- Share the src in the project directory file by adding its path on your machine to the list

#### I-D. Set up a dockerized development environment

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

#### I-E. Importing datasets

- In your command line, access smia CLI using the command below or version of it depanding on your command line <br />
  `docker exec -t -i user-interface bash`

#### I-E-1. Importing the small dummy test dataset

- Run test driver <br />
  `python test_driver.py`

Note! You might get a couple of warnings when building the user- and activity user graph, this is because the dummy dataset is very small and there is not enough labels in the training dataset for topic classification. The warnings can be ignored as this is just a dummy dataset for development and testing purposes.

#### I-E-2. Importing a real-life dataset from crawling Reddit

- Run reddit driver <br />
  `python reddit_driver.py`

- exit the CLI <br />
  `exit`

## II. Setting up the production environment
