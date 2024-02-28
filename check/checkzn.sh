#!/bin/bash

# Check if the worker node name is provided
if [ -z "$1" ]; then
    echo "Error: Worker node name not provided."
    exit 1
fi

# Set the threshold values for CPU and memory usage
CPU_THRESHOLD=1
MEMORY_THRESHOLD=1
csv_file="node_metrics.csv"
# Specify the worker node name from the command line argument
WORKER_NODE="$1"
check_node="$2"
pod="$3"

# Extract CPU and memory usage percentages for the specified worker node from the CSV file
CPU_USAGE=$(awk -F',' -v node="$check_node" 'NR>1 && $2 == node {gsub(/m|%/, "", $4); print $4}' "$csv_file")
MEMORY_USAGE=$(awk -F',' -v node="$check_node" 'NR>1 && $2 == node {gsub(/Mi|%/, "", $6); print $6}' "$csv_file")

# Remove percentages and convert to integers
CPU_USAGE=$(echo "$CPU_USAGE" | tr -d '%')
MEMORY_USAGE=$(echo "$MEMORY_USAGE" | tr -d '%')

# Check if CPU or memory usage exceeds the thresholds
if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ] && [ "$MEMORY_USAGE" -gt "$MEMORY_THRESHOLD" ]; then
    echo "yes"
    bash finding_n_n_z.sh "$check_node"
    bash finding_n_n_z.sh "$WORKER_NODE"
    # Run restorez.sh with the provided worker node name as an argument
    start_time=$(date +%s.%N)
    bash restorezn.sh "$WORKER_NODE" "$check_node"
    end_time=$(date +%s.%N)
    execution_time=$(echo "$end_time - $start_time" | bc)
    echo "$check_node,$WORKER_NODE,$execution_time" >> restore_z_n.csv
    python_script="delete.py"
    python3 "$python_script" "$pod"
    bash changetzn.sh "$check_node"
else
    echo "no"
fi
