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
num_pods=2

# Iterate over shuffled worker nodes and create pods
for ((i=0; i<num_pods; i++)); do
    worker_node=${shuffled_nodes[i]}
    for ((j=0; j<=0; j++)); do
        timestamp=$(date +%Y%m%d%H%M%S)
        cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod-worker${worker_node}-${j}-${timestamp}
  labels:
    app: nginx
spec:
  nodeName: worker${worker_node}
  containers:
    - name: nginx-container
      image: nginx:latest
EOF
    done
done
 sleep 100
done
