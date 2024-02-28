#!/bin/bash
# Check if worker node argument is provided
if [ -z "$1" ]; then
    echo "Error: Worker node name not provided."
    exit 1
fi

# Define variables
WORKER_NODE="$1"
NODE_NAME="$2"
NEW_POD_NAME="new-zookeeper-pod$WORKER_NODE-$(date +%Y%m%d%H%M%S)"
ZK_IMAGE="digitalwonderland/zookeeper"  # Replace with your ZooKeeper image and tag
BACKUP_FILE="new_filename.tar"
BACKUP_DEST_PATH="/tmp/$BACKUP_FILE"
ZK_EXEC_PATH="/opt/zookeeper/bin/zkServer.sh"

# Step 1: Create a new ZooKeeper pod on the specified worker node
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
    kubernetes.io/hostname: $WORKER_NODE

EOF
start_time=$(date +%s.%N)

while [ "$(kubectl get pod $NEW_POD_NAME -o jsonpath='{.status.phase}')" != "Running" ]; do
    echo "Waiting for the pod to be in the 'Running' state..."
    sleep 1
done

end_time=$(date +%s.%N)
execution_time=$(echo "$end_time - $start_time" | bc)
echo "$check_node,$WORKER_NODE,$execution_time" >> podrun_s_t.csv
kubectl cp checkpointnew/$BACKUP_FILE $NEW_POD_NAME:$BACKUP_DEST_PATH

start_time2=$(date +%s.%N)
# Step 3: Access the new pod and restore the backup
kubectl exec $NEW_POD_NAME -- /bin/bash -c "cd /tmp && tar -xvf $BACKUP_DEST_PATH"


# Step 4: Start ZooKeeper in the new pod
kubectl exec $NEW_POD_NAME -- /bin/bash -c "$ZK_EXEC_PATH start"
end_time2=$(date +%s.%N)
execution_time2=$(echo "$end_time2 - $start_time2" | bc)
echo "$node_name,$WORKER_NODE,$execution_time2" >> extract_s_t.csv
