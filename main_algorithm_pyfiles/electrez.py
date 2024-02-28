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

def electre_iii_method(decision_matrix, concordance_thresholds, discordance_thresholds):
    concordance_matrix = (decision_matrix >= concordance_thresholds).astype(int)
    discordance_matrix = (decision_matrix <= discordance_thresholds).astype(int)

    concordance_score = np.sum(concordance_matrix, axis=1)
    discordance_score = np.sum(discordance_matrix, axis=1)

    outranking_score = concordance_score - discordance_score

    return outranking_score

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

# Define criteria weights for TOPSIS
criteria_weights_topsis = {
    'CPU(%)': 0.5,
    'Memory(%)': 0.5
}

# Define concordance and discordance thresholds for ELECTRE III
concordance_thresholds = np.array([0.5, 0.7])  # Adjust these thresholds as needed
discordance_thresholds = np.array([0.2, 0.3])  # Adjust these thresholds as needed

# Specify the window size
window_size = 21

# Divide the dataset into windows
chunks = [df[i:i + window_size] for i in range(0, len(df), window_size)]

# Process each window
for chunk_df in chunks:
    # Normalize criteria for TOPSIS
    normalized_cpu_topsis = normalize_criteria(chunk_df['CPU(%)'])
    normalized_memory_topsis = normalize_criteria(chunk_df['Memory(%)'])

    # Create the decision matrix for TOPSIS
    decision_matrix_topsis = pd.DataFrame({
        'CPU(%)': normalized_cpu_topsis,
        'Memory(%)': normalized_memory_topsis
    })

    # Calculate TOPSIS scores
    distance_to_ideal = np.linalg.norm(decision_matrix_topsis - decision_matrix_topsis.max())
    distance_to_anti_ideal = np.linalg.norm(decision_matrix_topsis - decision_matrix_topsis.min())
    closeness_topsis = distance_to_anti_ideal / (distance_to_ideal + distance_to_anti_ideal)

    # Add the 'Closeness' column to the DataFrame
    chunk_df = chunk_df.copy()
    chunk_df['Closeness_TOPSIS'] = closeness_topsis

    #chunk_df.loc[:, 'Closeness_TOPSIS'] = closeness_topsis

    # Use ELECTRE III for further ranking within the group
    outranking_score_electre = electre_iii_method(decision_matrix_topsis.values, concordance_thresholds, discordance_thresholds)

    # Add the 'Outranking_Score_ELECTRE' column to the DataFrame
    #chunk_df.loc[:, 'Outranking_Score_ELECTRE'] = outranking_score_electre
    chunk_df['Outranking_Score_ELECTRE'] = outranking_score_electre

    # Rank nodes based on TOPSIS and ELECTRE III scores
#    ranked_nodes_topsis = chunk_df.sort_values(by='Closeness_TOPSIS', ascending=False)['Node'].tolist()
    ranked_nodes_electre = chunk_df.sort_values(by='Outranking_Score_ELECTRE', ascending=False)['Node'].tolist()

    # Display the ranked nodes for the current window
    print(f"\nRanked Nodes ELECTRE III (Window {len(chunks)}):")
    for i, node in enumerate(ranked_nodes_electre, start=1):
        print(f"{i}. {node}")
    node_name = ranked_nodes_electre[0]
#    b1 = 'finding_n_e_z.sh'
 #   run_bash_script(b1, [node_name])
  #  run_bash_script(b1, [ranked_nodes_electre[-1]])
    zookeeper_pods = get_zookeeper_pods_on_node(node_name)
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
    bash_script_path = 'checktryze.sh'
    print(f"the selected node to checkpoint :{node_name}")
    start_time = time.time()
    run_bash_script(bash_script_path, [node_name,picked_zookeeper_pod,ranked_nodes_electre[-1]])
    duration1 = time.time() - start_time
    print(f"Time Duration for the checkpoint script: {duration1} seconds")

    bash_s2 = 'checkze.sh'
    print(f"the selected pod to checkpoint :{ranked_nodes_electre[-1]}")
    run_bash_script(bash_s2, [ranked_nodes_electre[-1],node_name,picked_zookeeper_pod])
    durationt = time.time() - start_time
    duration2 = durationt - duration1
    print(f"Time Duration for the restore script: {duration2} seconds")
    print(f"Time Duration of totaal time : {durationt} seconds")
    csv_file_path = 'timeelectrez.csv'
    update_csv_file(csv_file_path, [node_name,ranked_nodes_electre[-1],durationt, duration1, duration2])
#    arguments = [picked_zookeeper_pod]
  #  bash3 = 'changetze.sh'
#    run_bash_script(bash3, [node_name])
 ##   subprocess.run(["python3", "delete.py"] + arguments)