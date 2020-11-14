#!/bin/bash


docker build -t orss_logicalbackup:ver1.0 .
docker run -d --name orss_logicalbackup -it orss_logicalbackup:ver1.0
docker exec -it orss_logicalbackup /bin/bash
