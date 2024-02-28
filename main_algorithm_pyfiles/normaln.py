import time,csv,sys
import subprocess
import random , re
import pandas as pd
import numpy as np
from kubernetes import client, config
def update_csv_file(file_path, row):
    with open(file_path, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(row)
def key_function(item):
    return int(item[1][:-1]) + int(item[2][:-2])
def get_nginx_pods_on_node(node_name):
    try:
        # Get the list of Nginx pods running on the specified node
        command = [
            'kubectl',
            'get',
            'pods',
            '--all-namespaces',
            f'--field-selector=spec.nodeName={node_name}',
            '-l', 'app=nginx',  # Adjust the label selector based on your deployment
            '-o', 'custom-columns=:metadata.name',
            '--no-headers'
        ]
        nginx_pods = subprocess.check_output(command, text=True).strip().split('\n')
        return nginx_pods
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None
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

def get_total_resources(metrics):
    # Parse CPU and memory metrics and calculate total resources
    try:
        cpu_usage, memory_usage = metrics.split()[1:3]
        cpu_usage = int(cpu_usage[:-1])  # Remove the trailing %
        memory_usage = int(memory_usage[:-2])  # Remove the trailing Mi
        total_resources = cpu_usage + memory_usage
        return total_resources
    except ValueError:
        return None

def run_bash_script(script_path, script_arguments):
    try:
        # Combine the 'bash' command with the script path and arguments
        command = ['bash', script_path] + script_arguments
        subprocess.run(command, check=True)
        print("Bash script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Bash script execution failed. {e}")

def process_nodes(first_node, last_node):
    nginx_pods = get_nginx_pods_on_node(last_node)
    picked_nginx_pod = None
#    b1 = 'finding_n_n_n.sh'
 #   run_bash_script(b1, [last_node])
  #  run_bash_script(b1, [first_node])
    pod_resources = []

    sorted_l=[]
    picked_nginx_pod = None  # Initialize the variable

    if len(nginx_pods) > 0:
        pod_resources = []

        for pod in nginx_pods:
            metrics = get_pod_metrics(pod)
            if metrics:
                cpu_usage, memory_usage = extract_cpu_memory_usage(metrics)
                if cpu_usage is not None and memory_usage is not None:
                    pod_resource = [pod, cpu_usage, memory_usage]
                    pod_resources.append(pod_resource)

    # Sort pods based on total resources
        sorted_l = sorted(pod_resources, key=key_function,reverse=True)
    else:
        print(f"Failed to retrieve nginx pods running on node '{node_name}'.")
        return
    
    picked_nginx_pod = sorted_l[0][0]

    # Rest of your code here
    bash_script_path = 'checktrynn.sh'
    print(f"the selected node to checkpoint :{last_node}")
    start_time = time.time()
    run_bash_script(bash_script_path, [last_node, picked_nginx_pod,first_node])
    duration1 = time.time() - start_time
    print(f"Time Duration for the checkpoint script: {duration1} seconds")

    bash_s2 = 'checknn.sh'
    print(f"the selected pod to checkpoint :{first_node}")
    run_bash_script(bash_s2, [first_node,last_node,picked_nginx_pod])
    durationt = time.time() - start_time
    duration2 = durationt - duration1
    print(f"Time Duration for the restore script: {duration2} seconds")
    print(f"Time Duration of total time : {durationt} seconds")
    csv_file_path = 'timenormaln.csv'
    update_csv_file(csv_file_path, [last_node,first_node,durationt, duration1, duration2])
#    arguments = [picked_nginx_pod]
 #   bash3 = 'changetnn.sh'
#    run_bash_script(bash3, [node_name])
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
