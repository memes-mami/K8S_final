import sys
import csv
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

# Get the existing data from pods_c.csv
csv_file = "pods_e_z.csv"
with open(csv_file, mode='r') as file:
    reader = csv.reader(file)
    rows = [row for row in reader]

zp = get_zookeeper_pods_on_node(node_name)
if zp == 0:
    print("None")
else:
    print(f"The number of Zookeeper pods on node {node_name} is: {zp}")

    # Append the number of Zookeeper pods as a third column to the last row
    rows[-1].extend([node_name, zp])

    # Save the updated data to pods_c.csv
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print(f"Data saved to {csv_file}")
