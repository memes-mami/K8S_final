#!/bin/bash

for i in {1..21}; do
  # Replace "X" with the current worker node number
  sed "s/workerX/worker$i/g" pod-template.yaml > access-checkpoint-worker$i.yaml

  # Apply the generated YAML file to create the pod
  kubectl apply -f access-checkpoint-worker$i.yaml

  # Optionally, you can remove the generated YAML file if not needed
  rm access-checkpoint-worker$i.yaml
done
