#!/bin/bash

IMAGE_NAME="${PWD##*/}_check"
if [ $# -eq 0 ]; then
   docker build -t $IMAGE_NAME . &> /dev/null
else
   docker build -t $IMAGE_NAME .
fi
docker run -v $PWD:/app -i $IMAGE_NAME
