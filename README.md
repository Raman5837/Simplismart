# Simplismart

Simplismart Assignment

---

## Features

1. **User Authentication and Organization Management**:

   - **User Authentication**: Users can authenticate using a basic username and password mechanism.
   - **Invite Code**: New users can join an organization only if they have a valid invite code.
   - **Organization Membership**: Once authenticated, users are automatically added to an organization.

2. **Cluster Management**:

   - **Cluster Creation**: Users can create and manage clusters, which are defined with fixed resources such as CPU, RAM, and GPU.
   - **Resource Management**: Tracks available and allocated resources for each cluster to ensure efficient utilization.

3. **Deployment Management**:

   - **Create Deployment**: Users can create a deployment request for a specific cluster, specifying the Docker image path, required CPU, GPU, and RAM resources.
   - **Resource Allocation for Deployment**: Each deployment request will consume a specific amount of resources from the cluster. If resources are insufficient, the deployment will be queued.
   - **Queue Deployments**: Deployments are queued in Redis if there are insufficient resources in the cluster.

4. **Scheduling Algorithm**:
   The scheduling algorithm optimizes deployment execution based on the following factors:
   - **Priority**: Deployments with higher priority should be scheduled first.
   - **Resource Utilization**: The system maximizes the usage of available resources in the cluster.
   - **Maximize Successful Deployments**: The system aims to maximize the number of deployments that can be successfully scheduled from the queue, balancing resource allocation efficiently.

---

## Requirements:

1. **Python 3.10+**.
2. **SQLite** for the database.
3. **Docker** and **Docker Compose**.
4. **Gunicorn** for running Django in production.
5. **Redis** for Celery message broker and storage.

---

## Project Setup

### Step 1: Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/Raman5837/Simplismart.git
cd Simplismart
```

## Step 2: Setup `.env` File

Create a `.env` file in the root directory of the project. Use the `.env.sample` file as an example.

You can copy the sample content and adjust it according to your environment.

### Step 3: Running the Project

#### Option 1:

- _Setup and Activate the Virtual Environment_

- Install Dependencies `python -m pip install -r requirements.txt`

- Create Migrations `python manage.py makemigrations`

- Run Migrations `python manage.py migrate`

- Run API Server `python manage.py runserver`

- Run Redis Server `redis-server`

- Run Celery Worker `python -m celery -A hypervisor worker --loglevel=info`

- Run Celery Beat Worker ` python -m celery -A hypervisor beat --loglevel=info`

- Run Test Cases `python manage.py test`

  - Note:- Redis connection is required to run few test cases

#### Option 2:

1. **Build the Docker Containers:**

   First, you need to build the Docker images for the application using
   `docker-compose build`

2. **Run the Docker Containers**

   Once the images are built, start the containers using `docker-compose up`

   This will start all the services, including:

   - **API server (Django)**

   - **Redis (for celery and caching)**

   - **Celery Beat (for scheduled tasks)**

   - **Celery worker (for background task processing)**

**Access Logs**:

To view the logs of a specific container, use the following command:

`docker-compose logs -f <container_name>`
