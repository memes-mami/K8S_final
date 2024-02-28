#!/bin/bash
while true; do
# Function to shuffle an array
shuffle() {
    local i tmp size arr
    arr=("$@")
    size=${#arr[@]}
    for ((i=size-1; i>0; i--)); do
        j=$((RANDOM % (i + 1)))
        tmp=${arr[i]}
        arr[i]=${arr[j]}
        arr[j]=$tmp
    done
    echo "${arr[@]}"
}

# Worker node numbers
worker_nodes=(1 2 3 4  6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21)

# Shuffle worker node numbers
shuffled_nodes=($(shuffle "${worker_nodes[@]}"))

# Number of pods to add
num_pods=1

# Iterate over shuffled worker nodes and create pods
for ((i=0; i<num_pods; i++)); do
    worker_node=${shuffled_nodes[i]}
    timestamp=$(date +%Y%m%d%H%M%S)
    for W in {1..1}; do
    NEW_POD_NAME="zookeeper-pod-worker${worker_node}-$timestamp"
    ZK_IMAGE="digitalwonderland/zookeeper"  # Replace with your ZooKeeper image and tag

    # Create a new ZooKeeper pod on the current worker node
    kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: $NEW_POD_NAME
spec:
  containers:
  - name: zookeeper
    image: $ZK_IMAGE
    ports:
    - containerPort: 2181
    - containerPort: 2888
    - containerPort: 3888
  nodeSelector:
    kubernetes.io/hostname: worker${WORKER_NODE}

EOF
done
done
 sleep 100
done
