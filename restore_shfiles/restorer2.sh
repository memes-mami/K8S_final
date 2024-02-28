#!/bin/bash

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

# Step 1: Create a new Redis pod on the specified worker node using a unique StatefulSet name
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-$WORKER_NODE
spec:
  serviceName: redis-$WORKER_NODE
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      initContainers:
      - name: config
        image: $REDIS_IMAGE
        command: [ "sh", "-c" ]
        args:
          - |
            cp /tmp/redis/redis.conf /etc/redis/redis.conf
            
            echo "finding master..."
            MASTER_FDQN=`hostname -f | sed -e 's/redis-[0-9]\./redis-0./'`
            if [ "$(redis-cli -h sentinel -p 5000 ping)" != "PONG" ]; then
              echo "master not found, defaulting to redis-0"

              if [ "$(hostname)" == "redis-0" ]; then
                echo "this is redis-0, not updating config..."
              else
                echo "updating redis.conf..."
                echo "slaveof $MASTER_FDQN 6379" >> /etc/redis/redis.conf
              fi
            else
              echo "sentinel found, finding master"
              MASTER="$(redis-cli -h sentinel -p 5000 sentinel get-master-addr-by-name mymaster | grep -E '(^redis-\d{1,})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})')"
              echo "master found : $MASTER, updating redis.conf"
              echo "slaveof $MASTER 6379" >> /etc/redis/redis.conf
            fi
        volumeMounts:
        - name: redis-config
          mountPath: /etc/redis/
        - name: config
          mountPath: /tmp/redis/
      containers:
      - name: redis
        image: $REDIS_IMAGE
        command: ["redis-server"]
        args: ["/etc/redis/redis.conf"]
        ports:
        - containerPort: 6379
          name: redis
        volumeMounts:
        - name: data
          mountPath: /data
        - name: redis-config
          mountPath: /etc/redis/
      volumes:
      - name: redis-config
        emptyDir: {}
      - name: config
        configMap:
          name: redis-config
EOF

# Add sleep to wait for the StatefulSet pods to be created
sleep 10

# Step 2: Copy the backup file into the new pod
kubectl cp checkpointw/$BACKUP_FILE $NEW_POD_NAME:$BACKUP_DEST_PATH

# Step 3: Access the new pod and restore the backup
kubectl exec $NEW_POD_NAME -- /bin/sh -c "cd /tmp && tar -xvf $BACKUP_DEST_PATH"

# Step 4: Start Redis in the new pod
kubectl exec $NEW_POD_NAME -- /bin/sh -c "$REDIS_EXEC_PATH /etc/redis/redis.conf"

# Add additional steps if necessary for your Redis setup
