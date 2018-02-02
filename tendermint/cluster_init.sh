#!/bin/bash
# Simple file to run neccesairy commands to reset cluster configuration
rm -rf ./.data
docker-compose -f docker-compose-cluster.yml down -v
docker-compose -f docker-compose-cluster-init.yml up
