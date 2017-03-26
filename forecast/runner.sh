#!/bin/bash
for i in `seq 1 129`;
do
        echo "Running item number" $i
        /home/manns/anaconda3/envs/tensor_flow_env_35/bin/python /home/manns/PycharmProjects/PythonForecasting/forecast/main.py ${i}
done