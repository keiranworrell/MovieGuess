#!/usr/bin/env bash

while IFS= read -r line; do
    id=`echo $line | cut -f1 -d','`
    name=`echo $line | cut -f2 -d','`
    act1=`echo $line | cut -f3 -d','`
    act2=`echo $line | cut -f4 -d','`
    act3=`echo $line | cut -f5 -d','`
    act4=`echo $line | cut -f6 -d','`
    act5=`echo $line | cut -f7 -d','`
    echo "Adding $id: $name"
    aws dynamodb put-item \
        --table-name movieActors \
        --item "{
  \"id\": {
    \"S\": \"${id}\"
  },
  \"filmName\": {
    \"S\": \"${name}\"
  },
  \"actor1\": {
    \"S\": \"${act1}\"
  },
  \"actor2\": {
    \"S\": \"${act2}\"
  },
  \"actor3\": {
    \"S\": \"${act3}\"
  },
  \"actor4\": {
    \"S\": \"${act4}\"
  },
  \"actor5\": {
    \"S\": \"${act5}\"
  }
}"
done < moviesData.csv