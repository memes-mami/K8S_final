#!/bin/bash
# Check if worker node argument is provided
if [ -z "$1" ]; then
    echo "Error: Worker node name not provided."
    exit 1
fi

# Define variables
WORKER_NODE="$1"
NEW_POD_NAME="new-redis-pod$WORKER_NODE"
REDIS_IMAGE="redis:6.2.3-alpine"  # Replace with your Redis image and tag
BACKUP_FILE="new_filename.tar"
BACKUP_DEST_PATH="/tmp/$BACKUP_FILE"
REDIS_EXEC_PATH="redis-server"

# Step 1: Create a new Redis pod on the specified worker node
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: $NEW_POD_NAME
spec:
  containers:
  - name: redis
    image: $REDIS_IMAGE
    ports:
    - containerPort: 6379
  nodeSelector:
    kubernetes.io/hostname: $WORKER_NODE

EOF

while [ "$(kubectl get pod $NEW_POD_NAME -o jsonpath='{.status.phase}')" != "Running" ]; do
    echo "Waiting for the pod to be in the 'Running' state..."
    sleep 1
done

# Step 2: Copy the backup file into the new pod
kubectl cp checkpointw/$BACKUP_FILE $NEW_POD_NAME:$BACKUP_DEST_PATH

# Step 3: Access the new pod and restore the backup
kubectl exec $NEW_POD_NAME -- /bin/sh -c "cd /tmp && tar -xvf $BACKUP_DEST_PATH"

# Step 4: Start Redis in the new pod
kubectl exec $NEW_POD_NAME -- /bin/sh -c "$REDIS_EXEC_PATH /etc/redis/redis.conf"

# Add additional steps if necessary for your Redis setup
