#!/bin/bash

for _ in {1..3}
do

curl --location --request GET 'http://localhost:8080/function/gpt2' \
--header 'Content-Type: text/plain' \
--data '你好'

done

# curl --location --request GET 'http://localhost:8080/function/sd' \
# --header 'Content-Type: text/plain' \
# --data 'a young girl is walking down the street.'
