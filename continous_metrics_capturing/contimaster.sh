#!/bin/bash

# Infinite loop to continuously print metrics every 5 seconds
while true; do
  # Get the current date and time for timestamp
  timestamp=$(date +"%Y-%m-%d %H:%M:%S")

  # Print CSV header once at the beginning
  if [ ! -e "header_printed" ]; then
    echo "Timestamp,Node,CPU(cores),CPU(%),Memory(bytes),Memory(%)"
    touch "header_printed"
  fi

  # Get metrics for the "master" node
  kubectl top nodes --no-headers | grep "master" | while read node cpu_mem; do
    # Extract CPU and memory values
    IFS=' ' read -ra metrics <<< "$cpu_mem"
    cpu_cores=${metrics[0]}
    cpu_percent=${metrics[1]}
    memory_bytes=${metrics[2]}
    memory_percent=${metrics[3]}

    # Append the metrics to the file
    echo "$timestamp,$node,$cpu_cores,$cpu_percent,$memory_bytes,$memory_percent" >> metricz-m.csv
  done

  # Sleep for 5 seconds before the next iteration
  sleep 15
done
