#!/bin/bash

IMAGE_NAME="${PWD##*/}_check"
docker build -t $IMAGE_NAME . &> /dev/null
docker run -v $PWD:/app -i $IMAGE_NAME
