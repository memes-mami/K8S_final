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


def normalize_criteria(criteria):
    return criteria / np.linalg.norm(criteria)

def vikor_method(decision_matrix, weights, v, s):
    s_p = np.min(decision_matrix, axis=1)
    s_n = np.max(decision_matrix, axis=1)

    r_p = np.max(decision_matrix - s_p[:, np.newaxis], axis=1)
    r_n = np.max(s_n[:, np.newaxis] - decision_matrix, axis=1)

    weights_reshaped = np.array(weights).reshape(1, -1)

    Q_p = weights_reshaped * (decision_matrix - s_p[:, np.newaxis]) / (r_p[:, np.newaxis] + 0.000001)
    Q_n = weights_reshaped * (s_n[:, np.newaxis] - decision_matrix) / (r_n[:, np.newaxis] + 0.000001)

    Q_p_star = np.max(Q_p, axis=1)
    Q_n_star = np.max(Q_n, axis=1)

    S = v * (Q_p / Q_p_star[:, np.newaxis]) + (1 - v) * (Q_n / Q_n_star[:, np.newaxis])

    R = np.argsort(S, axis=1)

    Q = np.min(S, axis=1)

    R_star = np.argsort(Q)

    performance_score = s * R[:, 0] + (1 - s) * R_star

    return performance_score

def process_window(chunk_df):
    normalized_cpu_vikor = normalize_criteria(chunk_df['CPU(%)'])
    normalized_memory_vikor = normalize_criteria(chunk_df['Memory(%)'])

    decision_matrix_vikor = pd.DataFrame({
        'CPU(%)': normalized_cpu_vikor,
        'Memory(%)': normalized_memory_vikor
    })

    performance_score_vikor = vikor_method(
        decision_matrix_vikor.values,
        list(criteria_weights_vikor.values()),
        v,
        s
    )

    chunk_df = chunk_df.copy()
    chunk_df.loc[:, 'Performance_Score_VIKOR'] = performance_score_vikor

    ranked_nodes_vikor = chunk_df.sort_values(by='Performance_Score_VIKOR', ascending=False)['Node'].tolist()

    print(f"\nRanked Nodes VIKOR (Window {len(chunks)}):")
    for i, node in enumerate(ranked_nodes_vikor, start=1):
        print(f"{i}. {node}")

    ranked_workers_vikor = ranked_nodes_vikor
    node_name = ranked_workers_vikor[0]
   # b1 = 'finding_n_v_z.sh'
    #run_bash_script(b1, [node_name])
    #run_bash_script(b1, [ranked_nodes_vikor[-1]])
    zookeeper_pods = get_zookeeper_pods_on_node(node_name)
    picked_zookeeper_pod = None
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
        return
    picked_zookeeper_pod = sorted_list[0][0]

    # Rest of your code here
    bash_script_path = 'checktryzv.sh'
    print(f"the selected node to checkpoint :{node_name}")
    start_time = time.time()
    run_bash_script(bash_script_path, [node_name, picked_zookeeper_pod,ranked_workers_vikor[-1]])
    duration1 = time.time() - start_time
    print(f"Time Duration for the checkpoint script: {duration1} seconds")

    bash_s2 = 'checkzv.sh'
    print(f"the selected pod to checkpoint :{ranked_workers_vikor[-1]}")
    run_bash_script(bash_s2, [ranked_workers_vikor[-1],node_name,picked_zookeeper_pod])
    durationt = time.time() - start_time
    duration2 = durationt - duration1
    print(f"Time Duration for the restore script: {duration2} seconds")
    print(f"Time Duration of total time : {durationt} seconds")
    csv_file_path = 'timevikorz.csv'
    update_csv_file(csv_file_path, [node_name, ranked_nodes_vikor[-1],durationt, duration1, duration2])
#    arguments = [picked_zookeeper_pod]
 #   bash3 = 'changetzv.sh'
#    run_bash_script(bash3, [node_name])
 #   subprocess.run(["python3", "delete.py"] + arguments)

# Load the dataset from CSV file
csv_file_path = 'node_metrics.csv'
df = pd.read_csv(csv_file_path)

# Replace '<unknown>' with NaN
df.replace('<unknown>', np.nan, inplace=True)

# Handle % in CPU and Memory columns
df['CPU(%)'] = df['CPU(%)'].str.rstrip('%').astype(float) / 100.0
df['Memory(%)'] = df['Memory(%)'].str.rstrip('%').astype(float) / 100.0

# Drop rows with NaN values
df.dropna(subset=['CPU(%)', 'Memory(%)'], inplace=True)

# Exclude the 'master' node
df = df[df['Node'] != 'master']

# Define criteria weights for VIKOR
criteria_weights_vikor = {
    'CPU(%)': 0.5,
    'Memory(%)': 0.5
}

# Specify the parameters for VIKOR
v = 0.5  # VIKOR "v" parameter (0 <= v <= 1)
s = 0.5  # VIKOR "s" parameter (0 <= s <= 1)

# Specify the window size
window_size = 21

# Divide the dataset into windows
chunks = [df[i:i + window_size] for i in range(0, len(df), window_size)]

# Process each window
for chunk_df in chunks:
    process_window(chunk_df)
