#!/bin/bash

# Accept the NODE_NAME as an argument
NODE_NAME="$1"

if [ -z "$NODE_NAME" ]; then
    echo "Usage: $0 <node-name>"
    exit 1
fi

INTERNAL_IP=$(kubectl get nodes "$NODE_NAME" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')

if [ -z "$INTERNAL_IP" ]; then
    echo "Internal IP not found for node '$NODE_NAME'"
    exit 1
fi

echo "Internal IP of node '$NODE_NAME': $INTERNAL_IP"

# Accept the POD_NAME as an argument
POD_NAME="$2"

if [ -z "$POD_NAME" ]; then
    echo "Usage: $0 <node-name> <pod-name>"
    exit 1
fi

# Replace path/to/folder with the actual path of the folder where checkpoint files are stored
folder_path="/var/lib/kubelet/checkpoints"

# Use the find command to delete all files and folders in the specified folder
find "$folder_path" -mindepth 1 -delete

POD_JSON=$(kubectl get pod $POD_NAME -o json)

# Extract the name, container names, and namespace of the specific pod using jq
containers=$(echo "$POD_JSON" | jq -r '.spec.containers[].name')
namespace=$(echo "$POD_JSON" | jq -r '.metadata.namespace')

# Capture the start time


# Perform the checkpointing using curl (replace with the actual curl command you need)
checkpoint_url="https://$INTERNAL_IP:10250/checkpoint/$namespace/$POD_NAME/$containers"
start_time=$(date +%s.%N)
curl_output=$(curl -sk -X POST "$checkpoint_url" \
  --key /etc/kubernetes/pki/apiserver-kubelet-client.key \
  --cacert /etc/kubernetes/pki/ca.crt \
  --cert /etc/kubernetes/pki/apiserver-kubelet-client.crt)

# Capture the end time
end_time=$(date +%s.%N)
execution_time=$(echo "$end_time - $start_time" | bc)
echo "$NODE_NAME,$POD_NAME,$execution_time" >> curl_s_e.csv
# Display the output of the curl command
echo "Curl command output:"
echo "$curl_output"

# Calculate and display the execution time
#execution_time=$(echo "$end_time - $start_time" | bc)
echo "Execution Time: $execution_time seconds"


# Extract the file location from the output JSON using jq
file_location=$(echo "$curl_output" | jq -r '.items[0]')
if [ -n "$file_location" ]; then
    echo "File Location: $file_location"

    # Extract the filename from the full path
    filename=$(basename "$file_location")

    kubectl cp access-checkpoint-"$NODE_NAME":/mnt/checkpoints/"$filename" checkpointnew/new_filename.tar
fi