# robotArm
# Robotic Task Execution System

This project allows you to control a **6-DOF robotic arm** using **task execution commands**. It leverages **Webots** for robot simulation, **RabbitMQ** for task messaging, and **GPT** for generating tasks.

![image](https://github.com/user-attachments/assets/e74886ad-9566-4dc8-989a-e58646350e95)

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

This system:
- Accepts tasks from the **high-level controller** (GPT).
- Executes these tasks on the robot (simulated using **Webots**).
- Communicates tasks asynchronously using **RabbitMQ**.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/mmahjoub5/robotArm.git
cd robotArm
```



### 2. Install Requirements
```bash
pip install poetry
poetry install --no-root
```


### 3. Download and Run RabbitMQ & MongoDB & Redis 
```bash
docker pull rabbitmq:management
docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management
```
```bash
docker pull mongo
docker run -d -p 27017:27017 mongo
```
```bash
docker pull redis
docker run --name redis-server -p 6379:6379 -d redis
```

### 4. Install Webots 
Install Webots from here [WEBOTS DOWNLOAD](https://cyberbotics.com/doc/guide/installation-procedure), and make sure it’s added to your system PATH.
Get python path from CLI with
``` bash
poetry run which python
```
Add python path in webots @Webots->Preferences->Python Command

## Usage

### Run Server 

```bash
poetry run uvicorn backend.app.main:app --reload
```





