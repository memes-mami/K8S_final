
num_pods=1
# Define variables

# Define variables
WORKER_NODE="$1"
#NODE_NAME="$2"
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


timeout=$((SECONDS + 60))
while [ "$(kubectl get pod $NEW_POD_NAME -o jsonpath='{.status.phase}')" != "Running" ]; do
    echo "Waiting for the pod to be in the 'Running' state..."
    sleep 1

    if [ $SECONDS -ge $timeout ]; then
        echo "Timeout reached. Exiting the loop."
        break
    fi
done




kubectl cp check/$BACKUP_FILE $NEW_POD_NAME:$BACKUP_DEST_PATH
end_time3=$(date +%s.%N)
kubectl exec $NEW_POD_NAME -- /bin/bash -c "cd /tmp && tar -xvf $BACKUP_DEST_PATH"
# Step 4: Start ZooKeeper in the new pod
kubectl exec $NEW_POD_NAME -- /bin/bash -c "$ZK_EXEC_PATH start"

echo "done"
sleep 100
done
