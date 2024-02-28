#!/bin/bash
while true; do
# Function to shuffle an array
shuffle() {
    local i tmp size arr
    arr=("$@")
    size=${#arr[@]}
    for ((i=size-1; i>0; i--)); do
        j=$((RANDOM % (i + 1)))
        tmp=${arr[i]}
        arr[i]=${arr[j]}
        arr[j]=$tmp
    done
    echo "${arr[@]}"
}

# Worker node numbers
worker_nodes=( 2 3 4 8 9 10 11 12 14 15 16 17 18 19 20 121)

# Shuffle worker node numbers
shuffled_nodes=($(shuffle "${worker_nodes[@]}"))

# Number of pods to addodes[0]}"
bash contizoo.sh "worker${shuffled_nodes}"
 sleep 120
done
