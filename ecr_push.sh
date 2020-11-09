#!/bin/bash

ECR_URI=933432669293.dkr.ecr.ap-northeast-1.amazonaws.com
REPOSITORY=koizumi-dev-repository-1

docker build -t 

aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI}
docker tag ${REPOSITORY}:latest  ${ECR_URI}/${REPOSITORY}:latest 
docker push ${ECR_URI}/${REPOSITORY}:latest 