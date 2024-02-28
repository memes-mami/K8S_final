#!/bin/bash

# Check if the node name is provided as an argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <node-name>"
    exit 1
fi

# Assign the node name from the command line argument
node_name=$1

# Use kubectl to get the number of Nginx pods on the specified node
nginx_pod_count=$(kubectl get pods --field-selector spec.nodeName=$node_name -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.containers[0].name}{"\n"}{end}' | grep nginx | wc -l)

# Print the result
echo "Number of Nginx pods on node $node_name: $nginx_pod_count"

# Python script to get the number of Zookeeper pods on the specified node
python_script=$(cat << 'END'
import sys
from kubernetes import client, config

def get_zookeeper_pods_on_node(node_name):
    config.load_kube_config()  # Load the kubeconfig file

    v1 = client.CoreV1Api()
    # List all pods in the default namespace
    pod_list = v1.list_namespaced_pod(namespace="default")
    zookeeper_pods = []

    # Iterate over pods and identify Zookeeper pods on the specified node
    for pod in pod_list.items:
        if pod.spec.node_name == node_name and "zookeeper" in pod.metadata.name.lower():
            zookeeper_pods.append(pod.metadata.name)
    
    return len(zookeeper_pods)

# Check if the node name is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <node-name>")
    sys.exit(1)

# Get the node name from the command-line argument
node_name = sys.argv[1]

zp = get_zookeeper_pods_on_node(node_name)
if zp == 0:
    print("None")
else:
    print(f"The number of Zookeeper pods on node {node_name} is: {zp}")
END
)

# Execute the Python script
python3 -c "$python_script"
