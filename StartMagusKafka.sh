docker rm $(docker ps -a -q)
docker-machine start default
eval $(docker-machine env)
docker-machine regenerate-certs
docker run -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=`docker-machine ip \`docker-machine active\`` --env ADVERTISED_PORT=9092 spotify/kafka

