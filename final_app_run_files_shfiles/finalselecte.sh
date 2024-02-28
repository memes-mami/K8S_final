#!/bin/bash

# Infinite loop to continuously append metrics every 5 seconds
while true; do
  # Get the current date and time for timestamp
  input_file="predicted.csv"
output_file="predict.csv"

# Print header to the output file
header=$(head -n 1 "$input_file")
echo "$header" > "$output_file"

# Print every 20 rows starting from the second row to the output file
awk 'NR % 20 == 0 &&  NR > 1' "$input_file" >> "$output_file"

  # Execute the Python script
  python3 selectelectre.py

  # Sleep for 15 seconds before the next iteration
  sleep 45
done

