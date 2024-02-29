#!/bin/bash

# Specify the node name as an argument
NODE_NAME=$1

if [ -z "$NODE_NAME" ]; then
  echo "Error: Node name not provided."
  exit 1
fi

# Get the list of Zookeeper pods running on the specified node
ZK_PODS=$(kubectl get pods --all-namespaces --field-selector spec.nodeName=$NODE_NAME -l app=zookeeper1 -o custom-columns=:metadata.name)

if [ -z "$ZK_PODS" ]; then
  echo "No Zookeeper pods found on node '$NODE_NAME'."
  exit 0
fi

echo "Zookeeper pods running on node '$NODE_NAME':"
echo "$ZK_PODS"
