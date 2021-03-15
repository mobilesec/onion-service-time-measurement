# Tor Onion Service Timing Analysis</h3>


<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)


<!-- ABOUT THE PROJECT -->
## About The Project


In the course of this project, a timing analysis of the provisioning time of Onion Services versions 2 and 3 was carried out. The Docker container and all other required files can be found in this repo.

### Built With

* Docker
* Python
* Bash


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

The following software is needed in advance to run the container
* docker

To install docker, please follow the installation steps from the official documentation [Docker Installation](https://docs.docker.com/engine/install/)

### Installation

1. Clone the repo
```sh
git clone https://git.ins.jku.at/students/tor-docker.git
```
2. Init and update the submodule
```sh
git submodule init
git submodule update
```
3. Build the docker image
Change into the cloned folder timing-analysis-container and run the following command:

```sh
docker build . 
```

<!-- USAGE EXAMPLES -->
## Usage

To run a timing analysis for onion services, the following line can be used:

```sh
docker run -it --rm -v/<PATH/TO/LOCAL/FOLDER>:/results <CONTAINER_NAME> -v <VERSION>
```

Replace all <> entries with your values. The meaning of these fields is described below:

- PATH/TO/LOCAL/FOLDER -> Local folder where you want to put the analysis results
- CONTAINER_NAME -> Name of the container
- VERSION -> Version of Onion Services to be analysed (currently available: V2, V3, V3NE (non ephemeral), V3VN (V3 using the vanguards extension))




