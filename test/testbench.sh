#!/bin/bash

for _ in {1..10}
do

curl --location --request GET 'http://localhost:8080/function/gpt2' \
--header 'Content-Type: text/plain' \
--data '你好' &

done
