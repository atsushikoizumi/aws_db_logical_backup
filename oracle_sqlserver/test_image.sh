#!/bin/bash

# git lfs memo

tag_ver="orss_logicalbackup:ver1.0"

docker build -t ${tag_ver} .
containerid=`docker run -d -it ${tag_ver} /bin/bash`
docker exec -it ${containerid} /bin/bash
