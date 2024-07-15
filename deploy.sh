#!bin/bash

cd /home/peets/Documents/projects/moviehub || exit

make stop

git pull origin main

nohup make up &