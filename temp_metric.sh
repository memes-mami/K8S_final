#!/bin/bash

# Define the output CSV file
output_csv="temp_metric.csv"
echo "Timestamp,Node,CPU(cores),CPU(%),Memory(bytes),Memory(%)" > "$output_csv"

# Calculate the number of iterations
#iterations=$((duration / interval))
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

kubectl top nodes --no-headers | while read node cpu_mem; do
# Extract CPU and memory values
  IFS=' ' read -ra metrics <<< "$cpu_mem"
  cpu_cores=${metrics[0]}
  cpu_percent=${metrics[1]}
  memory_bytes=${metrics[2]}
  memory_percent=${metrics[3]}

    # Append to the CSV file
  echo "$timestamp,$node,$cpu_cores,$cpu_percent,$memory_bytes,$memory_percent" >> "$output_csv"
done
