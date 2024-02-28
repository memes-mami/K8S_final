#!/bin/bash

# Check if the worker node name is provided
if [ -z "$1" ]; then
    echo "Error: Worker node name not provided."
    exit 1
fi

# Set the threshold values for CPU and memory usage
CPU_THRESHOLD=7
MEMORY_THRESHOLD=7

# Specify the worker node name from the command line argument
WORKER_NODE="$1"

# Get current CPU and memory usage for the specified worker node
METRICS=$(kubectl top node $WORKER_NODE | tail -n +2)

# Extract CPU and memory usage percentages and remove '%' and 'm' characters
CPU_USAGE=$(echo "$METRICS" | awk '{print $2}' | tr -d '%m')
MEMORY_USAGE=$(echo "$METRICS" | awk '{print $3}' | tr -d '%m')

# Check if CPU or memory usage exceeds the thresholds
if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ] || [ "$MEMORY_USAGE" -gt "$MEMORY_THRESHOLD" ]; then
    echo "yes"

    # Run restorez.sh with the provided worker node name as an argument
    bash restorez.sh "$WORKER_NODE"
else
    echo "no"
fi
