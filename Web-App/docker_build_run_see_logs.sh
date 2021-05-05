# stop containers
docker stop $(docker ps -a -q) 

# remove containers
docker rm $(docker ps -a -q) && docker rmi $(docker images | grep '^<none>' | awk '{print $3}')

# build container
docker build . -f Dockerfile -t detectron2-webapp

# run contrainer on port 8080
docker run --name=detectron2_container -p 8080:8080 -e PYTHONUNBUFFERED=1 -d detectron2-webapp

# see logs
docker logs -f -t $(docker ps -a -q)