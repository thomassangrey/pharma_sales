#!/bin/bash
#
# Use this shell script to compile (if necessary) your code and then execute it. Below is an example of what might be found in this file if your program was written in Python
#
cd  src/modules/ 
python setup.py build_ext --inplace
cd ../../
declare -r N="100000"
head -${N} input/itcont.txt > input/itcont_1_pharma_sales.txt


python3.6 ./src/event_profiler.py 
