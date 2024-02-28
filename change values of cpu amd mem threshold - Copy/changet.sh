#!/bin/bash

# Set the CSV file name
csv_file="node_metrics.csv"

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <node>"
    exit 1
fi

node="$1"

# Check if the node exists in the CSV file
if ! grep -q "$node" "$csv_file"; then
    echo "Error: Node '$node' not found in the CSV file."
    exit 1
fi

# Extract CPU% and Memory% for the specified node and remove '%'
cpu_percentage=$(awk -F, -v node="$node" '$2==node {gsub("%","",$4); print $4}' "$csv_file")
memory_percentage=$(awk -F, -v node="$node" '$2==node {gsub("%","",$6); print $6}' "$csv_file")

sed -i "s/CPU_THRESHOLD=.*$/CPU_THRESHOLD=$cpu_percentage/" checkn.sh
sed -i "s/MEMORY_THRESHOLD=.*$/MEMORY_THRESHOLD=$memory_percentage/" checkn.sh

echo "Thresholds updated successfully."
