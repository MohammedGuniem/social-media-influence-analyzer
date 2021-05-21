# Social Media Influence Analyzer

This is a project in social media influence analysis using Computer Science to detect and classify influences between users of social media. The project is carried out by Mohammed Z. Guniem to acheive the objective of his master thesis in producing a secure and reliable system for detecting and classifying influences between users on social media platforms.

This repository contains all project code, documents and other related files and folders.

To set up the project on your preffered enviornment, please follow the steps below

## I. Setting up the development environment

The development of this project is mainly based on Docker Technology, follow the steps below to set up an environment for development and testing purposes.

#### A. Clone or download the project code of this repository to your favorite location on your machine

- If cloning: Download and install the Git tool using this link https://git-scm.com/downloads
- If downloading directly: unzip the project files in your favorite location

#### B. Download Docker Desktop

- Download and install Docker Desktop using this link https://www.docker.com/products/docker-desktop
- Open Docker Desktop
- Go to Settings -> Resources -> File Sharing
- Share the src in the project directory file by adding its path on your machine to the list

#### C. Set up a dockerized development environment

- Open a command line window on you machine as an administrator, preferably git bash
- Navigate to your location in step A above
  `cd {your_location}`
- Now, navigate to your src code folder
  `cd src`
- Spin up all configured containers in the docker-compose.yml file process using attached mode
  `docker-compose up -d`
- Docker will now pull images for mongodb and neo4j and then set up the required services for this project.
- Docker will also build a user-interface image and run this project as a container with Python and its required packages installed.
- This might take a couple of minutes at the first time since pulling images is a little time-consuming
- Please wait for a couple of minutes depending on the capabilities of your system until the mongoDB and neo4j database services are up and running
- Then, go to localhost:5000 or host.docker.internal:5000 on your browser with javascript enabled.
- You should now be able to access the GUI interface of the project.

#### Importing datasets

- In your command line, access smia CLI using the command below or version of it depanding on your command line
  `docker exec -t -i user-interface bash`

#### A. Importing the small dummy test dataset

- Run test driver
  `python test_driver.py`

Note! You might get a couple of warnings when building the user- and activity user graph, this is because the dummy dataset is very small and there is not enough labels in the training dataset for topic classification. The warnings can be ignored as this is just a dummy dataset for development and testing purposes.

#### B. Importing a real-life dataset from crawling Reddit

- Run reddit driver
  `python reddit_driver.py`

- exit the CLI
  `exit`

## II. Setting up the production environment
