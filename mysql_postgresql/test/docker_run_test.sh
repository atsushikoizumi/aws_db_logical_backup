#!/bin/bash

docker build -t logicalbackup:test .
docker run --rm logicalbackup:test