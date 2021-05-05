# Detectron2 Web App

## Description

An interactive computer vision web app that wraps Detectron2's Mask R-CNN for instance segmentation on images. 

The app's backend is built using python and provides a web server hosted with python's flask framework.

The frontend is built using a standard DHTML tech stack including HTML, CSS, JavaScript

## Local Setup & Deployment

After installing a few dependencies, the app can be built and run on your local machine in minutes using docker. 

### Prerequisites

- Python3: https://www.python.org/downloads/
- Docker: https://docs.docker.com/engine/install/
- Git LFS Extension: https://git-lfs.github.com/
    - After downloading the installer, follow the instructions to enable Git LFS Extension in your Git user account
    - This extensions helps with large file storage in Git

* Note: These instructions assume a linux-based operating system. Although the docker container should still build properly on other systems, the installation steps may be different

After installing the prerequisites, follow the steps below to Build, Deploy, and Use the web app.

### Build 

1. change to your desired location and pull the repo
> $ cd ~/Git
> 
>$ git pull https://github.com/VarunSreenivasan16/CS766-Project.git

2. Change your working directory to the Web-App directory
> $ cd Web-App

3. Build the docker image, which will bundle all dependencies into the hosting container
> $ docker build . -f Dockerfile -t detectron2-webapp

* Note: If you get error while building the image, the likely cause is a memory shortage within the container. You can fix this by adjusting the docker Preferences > Resources > Memory. At the time of submission, I have my preferences set to 15 GB and the container is building properly.

### Deploy

1. After pulling the repo and building the docker image, deploy the container locally with

> docker run --name=detectron2_container -p 8080:8080 -e PYTHONUNBUFFERED=1 -d detectron2-webapp

2. To view the logs of the server-side requests and processing, run

> docker logs -f -t $(docker ps -a -q)

### Use

1. The container and app should now be deployed locally, navigate to localhost:8080 in your browser (Chrome recommended) to begin processing your own images!

## AWS Setup & Deployment

### Prerequisites

### Installation

### Deployment 

### Usage

## Features in Progress

### Grabcut Inference

### Custom Model Training

## Authors

## Credits