#!/bin/bash

# Define the output CSV file
output_csv="node_metrics_trace.csv"

# Define the duration in seconds
duration=600000 # Collect metrics for 10 times, with 30 seconds between each collection

# Define the interval in seconds
interval=15  # Collect metrics every 30 seconds

# Create a CSV header
echo "Timestamp,Node,CPU(cores),CPU(%),Memory(bytes),Memory(%)" > "$output_csv"

# Calculate the number of iterations
iterations=$((duration / interval))

# Loop to collect metrics at 30-second intervals, 10 times
for ((i=1; i<=iterations; i++)); do
  # Get the current date and time for timestamp
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

  # Sleep for 30 seconds before the next iteration
  sleep $interval
done



