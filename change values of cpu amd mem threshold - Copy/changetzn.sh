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
if [ "$cpu_percentage" = "<unknown>" ]; then
    echo "CPU percentage is unknown. Exiting the script."
    exit 1  # Exit with an error status
fi

sed -i "s/CPU_THRESHOLD=.*$/CPU_THRESHOLD=$cpu_percentage/" checkzn.sh
sed -i "s/MEMORY_THRESHOLD=.*$/MEMORY_THRESHOLD=$memory_percentage/" checkzn.sh

echo "Thresholds updated successfully."

sed -i "s/CPU_THRESHOLD=.*$/CPU_THRESHOLD=$cpu_percentage/" checktryzn.sh
sed -i "s/MEMORY_THRESHOLD=.*$/MEMORY_THRESHOLD=$memory_percentage/" checktryzn.sh
