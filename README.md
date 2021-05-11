# graphAI_webapp

## Running the Development Environment
1. Create a file called "env" at ./ and enter the environmental variables as specified in ./env_example. There are 3 files to edit:
- database.env
- pgadmin.env
- jwtsecret.env
2. Edit the database.env and pgadmin.env files accordingly to your preference. However, we advise to set the JWT key to a randomly generated key which is at least 256 bit.
3. Skip this step if yarn is already installed globally. Otherwise, run the following command 
```
$ npm install --global yarn
```
4. Finally, deploy the docker containers 
```
$ docker-compose up
```
5. You can access the web-application at http://localhost:3000/
6. Removing the containers 
```
$ docker-compose down
```
 
## Deploying the Production Environment to Docker Swarm
1. Create a file called "env" at ./ and enter the environmental variables as specified in ./env_example. There are two files to edit:
- database.env
- pgadmin.env
2. Under ./db_api/, create a folder called "secrets.py" and fill in the environmental variables as stated in ./db_api/secrets_example.py
3. Skip to step 4 if yarn is already installed globally. Otherwise, run the following command 
```
$ npm install --global yarn
```
4. Skip to step 5 if you have already created the images 
```
$ docker-compose -f docker-compose.prod.yml up 
$ docker-compose -f docker-compose.prod.yml down --volumes
```
5. Finally, deploy the production environment
```
$ docker swarm init 
$ docker stack deploy --compose-file=docker-compose.prod.yml graphai_webapp
```
5. Check if the swarm service has been succesfully created via
```
$ docker service ls 
```
6. The output should ressemble the following:
```
ID             NAME                           MODE         REPLICAS   IMAGE                                 PORTS
y2ghlv164z26   graphai_webapp_api             replicated   1/1        127.0.0.1:5000/api:latest             *:5000->5000/tcp
xyxal0u2478d   graphai_webapp_db_api          replicated   1/1        127.0.0.1:5002/db_api:latest          *:5002->5002/tcp
v4gujlsiop0r   graphai_webapp_frontend_prod   replicated   1/1        127.0.0.1:3000/frontend_prod:latest   *:3000->80/tcp
3c88c2jm5rnp   graphai_webapp_gnn_api         replicated   1/1        127.0.0.1:5001/gnn_api:latest         *:5001->5001/tcp
cqbsc7pkn7en   graphai_webapp_login           replicated   1/1        127.0.0.1:5003/login:latest           *:5003->5003/tcp
rv57qu93h6ho   graphai_webapp_postgres        replicated   1/1        postgres:alpine                       *:5432->5432/tcp
```
- The container_id should ressemble a hash
7. You can access the web-application at http://localhost:3000/
8. Removing the swarm service
```
$ docker stack rm graphai_webapp
$ docker swarm leave -f
```

## Scalling using Docker Swarm
1. Run the following command 
```
$ docker service scale <service_name>=<scale_to_value>
```
2. <service_name> should represent the service you want to scale and <scale_to_value> would represent the amount of services we wish to replicate. For example, if we wish to scale the microservice communicating with the database to 2, we can run the following command. 
```
$ docker service scale graphai_webapp_db_api=2
```
3. After replication, you will notice that the REPLICAS count for the respective service has increased by the specified amount "docker service ls". Using the example above, we notice the following:
```
ID             NAME                           MODE         REPLICAS   IMAGE                                 PORTS
container_id   graphai_webapp_db_api          replicated   2/2        127.0.0.1:5002/db_api:latest          *:5002->5002/tcp
```

## Checking Access Logs using Docker Swarm
1. Run the following command 
```
$ docker service logs <service_name>
```
2. <service_name> should represent the service you want to scale, for example, if we wish to scale the microservice communicating with the database, we can run the following command
```
$ docker service logs graphai_webapp_db_api
```

## Using pgAdmin4 to Access the PostgreSQL Service. [ONLY USE IN DEVELOPMENT ENV]
1. In ./docker-compose.yml, uncomment the pgadmin service as seen below:
```
  # pgadmin:
  #   image: dpage/pgadmin4
  #   container_name: pgadmin
  #   env_file:
  #     - ./env/pgadmin.env
  #   ports:
  #     - "8080:80"
  #   depends_on:
  #     - postgres
  #   logging:
  #     driver: "none"
```
2. Run the following command 
```
$ docker-compose up pgadmin
```
3. To stop the pgAdmin4 service. Run the following command.
```
$ docker-compose stop pgadmin
```
