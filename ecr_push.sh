#!/bin/bash

echo -n "IMAGE_TAG: "
read IMAGE_TAG

if [ -z "${IMAGE_TAG}" ]; then
    echo "please set version."
    exit
fi

SCRIPT_DIR=$(cd $(dirname $0); pwd)
ECR_URI=532973931974.dkr.ecr.eu-north-1.amazonaws.com/koizumi-dev-logicalbackup

docker build -t ${ECR_URI}:${IMAGE_TAG} ${SCRIPT_DIR}
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI%.*}
docker push ${ECR_URI}:${IMAGE_TAG}
