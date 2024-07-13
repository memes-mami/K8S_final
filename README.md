
## Code Path Explanation

### Basic Workflow Using a Particular Algorithm

1. **Metrics Collection and Ranking**:
   - Collect the metrics (CPU and memory usage) of all worker nodes.
   - Use a specific algorithm (e.g., Electre-3, Vikor, Topsis) to rank these worker nodes based on the collected metrics.

2. **Threshold Check**:
   - Check if the metrics of the top-ranked node exceed a predefined threshold value.
   - If the metrics do not exceed the threshold, stop the process and proceed to the next cycle.
   - If the metrics exceed the threshold, proceed to the next steps.

3. **Pod Identification**:
   - List all the pods on the top-ranked node.
   - Identify the pod consuming the most resources (CPU + memory).
   - Save the name of this pod and its containers (note: the applications have a single container in each pod).

4. **Pod Migration**:
   - Migrate the identified pod from the top-ranked node to the least ranked node to reduce the load on the top-ranked node.

5. **Algorithm Variants**:
   - Multiple algorithms (Electre-3, Vikor, Topsis) are used to rank the nodes.
   - Perform migrations based on these rankings.

6. **Dynamic Threshold Adjustment**:
   - Dynamically change the threshold for migration.
   - If the top-ranked node's metrics exceed the threshold, update the threshold to the metrics value of the overloaded node.

### Experimental Setup

- **Frequency**:
  - Randomly add applications to the worker nodes.
  - Run the algorithm every 45 seconds to check the metrics and perform migrations if necessary.

- **Applications Tested**:
  - **Nginx**: A stateless application.
  - **Zookeeper**: A stateful application.

### Folder Contents

1. **Checktry**:
   - Files that check the metrics of the top-ranked node.
   - Continue the process of checkpointing if metrics exceed the threshold.

2. **Copy_tar**:
   - Files that measure the time taken to copy the checkpointed tar file to the newly created pod for migration.

3. **Curl**:
   - Files that measure the time taken for checkpointing the pod on the overloaded node.

4. **Extract**:
   - Files that measure the time taken to restore the tar file on the new node.

5. **Finding**:
   - Files that find the number of pods on a worker node.

6. **Pods_**:
   - Files that provide the number of pods on a worker node before and after migration.

7. **Restore_**:
   - Files that measure the total time taken for restoration.

8. **Startup_latency**:
   - Files that measure the time taken for the new pod to start running after deployment.

### Additional Notes

- **Access Pods**:
  - Used for obtaining the file from the worker node to the master node for migration.
  - There are multiple other methods available to perform this operation.

- **Setup**:
  - The `setup.txt` file contains the necessary commands to initialize the single Master multi-node cluster in Kubernetes.

- **Missing Files**:
  - Some required files might be missing. Please download all files from another branch named "all_files" to ensure you have all the necessary supporting files for performing the operations.
