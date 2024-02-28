import time,csv,sys
import subprocess
import random , re
import pandas as pd
import numpy as np
from kubernetes import client, config

def printm(migrations):

    migrations+=1
    update_csv_file(csv3, ["did migration", migrations])
    print(f"The no of migrations so far :{migrations}")

def update_csv_file(file_path, row):
    with open(file_path, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(row)
def update_threshold(s,value):
    if (s[0]>value[0]) and (s[1]>value[1]):
        value[0]=s[0]
        value[1]=s[1]
        return True
    else:
        return False


def key_function(item):
    return int(item[1][:-1]) + int(item[2][:-2])
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
csv_file_path = 'predict.csv'
csv3='migrations.csv'
df = pd.read_csv(csv_file_path)
migrations =0

# Define criteria weights for TOPSI
# Define concordance and discordance thresholds for ELECTRE III
concordance_thresholds = np.array([0.5, 0.7])  # Adjust these thresholds as needed
discordance_thresholds = np.array([0.2, 0.3])  # Adjust these thresholds as needed

# Specify the window size
window_size = 18
value=[1,1]

# Divide the dataset into windows
chunks = [df[i:i + window_size] for i in range(0, len(df), window_size)]

# Process each window
for chunk_df in chunks:
    chunk_df = chunk_df.copy()
    metric = 'getm.sh'
    run_bash_script(metric, [])


    csv2= 'metrics.csv'
    df2 = pd.read_csv(csv2)

    df2['CPU(%)'] = df2['CPU(%)'].replace({'%': ''}, regex=True).replace({'<unknown>': 0})
    df2['Memory(%)'] = df2['Memory(%)'].replace({'%': ''}, regex=True).replace({'<unknown>': 0})

# Convert columns to numeric
    df2['CPU(%)'] = pd.to_numeric(df2['CPU(%)'])

    df2['Memory(%)'] = pd.to_numeric(df2['Memory(%)'])
#    chunk_df['Node'] = ['worker' + str(i) for i in range(1, 22) if i != 5]
#    chunk_df[ 'Node'] = ['worker' + str(i) for i in range(2, 20) if i != 5 or i !=4]
 #   chunk_df['Node'] =['worker121']
    chunk_df['Node'] = ['worker' + str(i) for i in range(2, 21) if i not in (4, 5)] + ['worker121']
    # Add new columns with the sum of 'CPU(%)' and 'predicted_cpu_per', and 'Memory(%)' and 'predicted_mem_per'
    chunk_df[ 'predicted_cpu_per'] = df2['CPU(%)'] + chunk_df['predicted_cpu_per']
    chunk_df[ 'predicted_mem_per'] = df2['Memory(%)'] + chunk_df['predicted_mem_per']

    # Normalize criteria for TOPSIS
    normalized_cpu_topsis = normalize_criteria(chunk_df['predicted_cpu_per'])
    normalized_memory_topsis = normalize_criteria(chunk_df['predicted_mem_per'])

    # Create the decision matrix for TOPSIS
    decision_matrix_topsis = pd.DataFrame({
        'predicted_cpu_per': normalized_cpu_topsis,
        'predicted_mem_per': normalized_memory_topsis
    })

    # Calculate TOPSIS scores
    distance_to_ideal = np.linalg.norm(decision_matrix_topsis - decision_matrix_topsis.max())
    distance_to_anti_ideal = np.linalg.norm(decision_matrix_topsis - decision_matrix_topsis.min())
    closeness_topsis = distance_to_anti_ideal / (distance_to_ideal + distance_to_anti_ideal)

    # Add the 'Closeness' column to the DataFrame
#    chunk_df['Closeness_TOPSIS'] = closeness_topsis
    chunk_df.loc[:, 'Closeness_TOPSIS'] = closeness_topsis

    # Use ELECTRE III for further ranking within the group
    outranking_score_electre = electre_iii_method(decision_matrix_topsis.values, concordance_thresholds, discordance_thresholds)

    # Add the 'Outranking_Score_ELECTRE' column to the DataFrame
#    chunk_df['Outranking_Score_ELECTRE'] = outranking_score_electre
    chunk_df.loc[:, 'Outranking_Score_ELECTRE'] = outranking_score_electre

    # Rank nodes based on TOPSIS and ELECTRE III scores
    ranked_nodes_electre = chunk_df.sort_values(by='Outranking_Score_ELECTRE', ascending=False)['Node'].tolist()

    # Display the ranked nodes for the current window
    print(f"\nRanked Nodes ELECTRE III (Window {len(chunks)}):")
    for i, node in enumerate(ranked_nodes_electre, start=1):
        print(f"{i}. {node}")
    node_name = ranked_nodes_electre[0]
    s = chunk_df[chunk_df['Node'] == node_name][['predicted_cpu_per', 'predicted_mem_per']].values.tolist()[0]
    if update_threshold(s,value):
       
        script_arguments = [node_name]
        script_arguments2 = [ranked_nodes_electre[-1]]


        try:
            subprocess.run(["python3", "finding_s_e.py"] + script_arguments, check=True)
            subprocess.run(["python3", "finding_s_e.py"] + script_arguments2, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running other_script.py: {e}")
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
        bash_script_path = 'checktryse.sh'
        print(f"the selected node to checkpoint :{node_name}")
        start_time = time.time()
        run_bash_script(bash_script_path, [node_name,picked_zookeeper_pod])
        duration1 = time.time() - start_time
        print(f"Time Duration for the checkpoint script: {duration1} seconds")

        bash_s2 = 'checkse.sh'
        print(f"the selected pod to checkpoint :{ranked_nodes_electre[-1]}")
        run_bash_script(bash_s2, [ranked_nodes_electre[-1],picked_zookeeper_pod])
        durationt = time.time() - start_time
        duration2 = durationt - duration1
        print(f"Time Duration for the restore script: {duration2} seconds")
        print(f"Time Duration of total time : {durationt} seconds")
        csv_file_path = 'timeelectres.csv'
        update_csv_file(csv_file_path, [node_name,ranked_nodes_electre[-1],durationt, duration1, duration2])
        printm(migrations)
        #update_csv_file(csv3, ["did migration", migrations])

    time.sleep(45)
