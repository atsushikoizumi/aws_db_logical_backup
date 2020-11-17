#!/bin/bash

# git lfs memo

tag_ver="orss_logicalbackup:ver0.2"

docker build -t ${tag_ver} .
docker run ${tag_ver}
