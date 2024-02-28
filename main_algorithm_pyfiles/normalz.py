import time,csv,sys,re
import subprocess
import random
import pandas as pd
import numpy as np
from kubernetes import client, config

def key_function(item):
    return int(item[1][:-1]) + int(item[2][:-2])

def update_csv_file(file_path, row):
    with open(file_path, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(row)
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

    return zookeeper_pods

def get_pod_metrics(pod_name):
    try:
        # Get CPU and memory metrics for the pod
        command = ['kubectl', 'top', 'pod', pod_name]
        metrics = subprocess.check_output(command, text=True)
        return metrics
    except subprocess.CalledProcessError as e:
        print(f"Error fetching metrics for pod {pod_name}: {e}")
        return None

def extract_cpu_memory_usage(metrics):
    # Extract CPU and memory usage from the metrics
    match = re.search(r'(\d+m)\s+(\d+Mi)', metrics)
    if match:
        cpu_usage, memory_usage = match.groups()
        return cpu_usage, memory_usage
    else:
        return None, None



def run_bash_script(script_path, script_arguments):
    try:
        # Combine the 'bash' command with the script path and arguments
        command = ['bash', script_path] + script_arguments
        subprocess.run(command, check=True)
        print("Bash script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Bash script execution failed. {e}")



def get_zookeeper_pods_on_node(node_name):
    try:
        command = [
            'kubectl',
            'get',
            'pods',
            '--all-namespaces',
            f'--field-selector=spec.nodeName={node_name}',
            '-l', 'app=zookeeper',
            '-o', 'custom-columns=:metadata.name',
            '--no-headers'
        ]
        zk_pods = subprocess.check_output(command, text=True).strip().split('\n')
        return zk_pods
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

def run_bash_script(script_path, script_arguments):
    try:
        command = ['bash', script_path] + script_arguments
        subprocess.run(command, check=True)
        print("Bash script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Bash script execution failed. {e}")

def process_nodes(first_node, last_node):
    zookeeper_pods = get_zookeeper_pods_on_node(last_node)
    picked_zookeeper_pod = None
#    b1 = 'finding_n_n_z.sh'
 #   run_bash_script(b1, [last_node])
  #  run_bash_script(b1, [first_node])
    picked_zookeeper_pod = None  # Initialize the variable

    if len(zookeeper_pods) > 0:
        pod_resources = []

        for pod in zookeeper_pods:
            metrics = get_pod_metrics(pod)
            if metrics:
                cpu_usage, memory_usage = extract_cpu_memory_usage(metrics)
                if cpu_usage is not None and memory_usage is not None:
                    pod_resource = [pod, cpu_usage, memory_usage]
                    pod_resources.append(pod_resource)
    
    # Sort pods based on total resources
        sorted_list = sorted(pod_resources, key=key_function, reverse=True)
    else:
        print(f"Failed to retrieve Zookeeper pods running on node '{node_name}'.")
        continue
    picked_zookeeper_pod = sorted_list[0][0]

    # Rest of your code here
    bash_script_path = 'checktryzn.sh'
    print(f"the selected node to checkpoint :{last_node}")
    start_time = time.time()
    run_bash_script(bash_script_path, [last_node, picked_zookeeper_pod, first_node])
    duration1 = time.time() - start_time
    print(f"Time Duration for the checkpoint script: {duration1} seconds")

    bash_s2 = 'checkzn.sh'
    print(f"the selected pod to checkpoint :{first_node}")
    run_bash_script(bash_s2, [first_node,last_node,picked_zookeeper_pod])
    durationt = time.time() - start_time
    duration2 = durationt - duration1
    print(f"Time Duration for the restore script: {duration2} seconds")
    print(f"Time Duration of total time : {durationt} seconds")
    csv_file_path = 'timenormalz.csv'
    update_csv_file(csv_file_path, [last_node,first_node, durationt, duration1, duration2])
#    arguments = [picked_zookeeper_pod]
  #  bash3 = 'changetzn.sh'
 #   run_bash_script(bash3, [node_name])
 #   subprocess.run(["python3", "delete.py"] + arguments)

# Read the CSV file into a list of dictionaries
with open('node_metrics.csv', 'r') as file:
    reader = csv.DictReader(file)
    data = list(reader)

# Remove rows with '<unknown>' in the 'CPU(%)' column
filtered_data = [row for row in data if row['CPU(%)'] != '<unknown>']

# Sort the list based on the 'CPU(%)' column in ascending order
sorted_data = sorted(filtered_data, key=lambda x: float(x['CPU(%)'].rstrip('%')))

# Print the ascending order list
print("Ascending Order List based on CPU(%):")
for row in sorted_data:
    print(row)

# Determine the last node to extract
last_node = sorted_data[-1]['Node']
if last_node == 'master':
    last_node = sorted_data[-2]['Node']

# Extract the first and last nodes
first_node = sorted_data[0]['Node']
process_nodes(first_node, last_node)
