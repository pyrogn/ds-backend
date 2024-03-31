#!/bin/bash

commands=(
"curl -v -X GET http://51.250.19.218:8080/read_plate_single" # 400
"curl -v -X GET http://51.250.19.218:8080/read_plate_single?img_id=1" # 404
"curl -v -X GET http://51.250.19.218:8080/read_plate_single?img_id=9965" # 200
"curl -v -X POST http://51.250.19.218:8080/read_plate_multiple -H \"Content-Type: application/json\"" # 400
"curl -v -X POST http://51.250.19.218:8080/read_plate_multiple -H \"Content-Type: application/json\" -d '{\"img_ids\": [9965, 10022, 3]}'" # 200
)

for cmd in "${commands[@]}"; do
    echo "$cmd"
    output=$(eval "$cmd" 2>&1)
    echo "$output"
    echo
    echo
done
