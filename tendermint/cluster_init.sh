#!/bin/bash

rm -rf ./.data
docker-compose -f docker-compose-cluster.yml down -v
docker-compose -f docker-compose-cluster-init.yml up
