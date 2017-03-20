#!/bin/bash
for i in `seq 1 129`;
do
        echo "Running item number" $i
        /home/mannsi/pythonVirtualEnvs/bin/python /home/mannsi/code/PythonForecasting/forecast/main.py ${i}
done