import sys
import subprocess

def delete_pod(pod_name):
    try:
        subprocess.run(['kubectl', 'delete', 'pod', pod_name], check=True)
        print(f"Pod {pod_name} deleted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting pod {pod_name}: {e}")

# Check if a pod name is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <pod_name>")
    sys.exit(1)

# Get pod name from command-line argument
pod_name = sys.argv[1]

# Call the function to delete the specified pod
delete_pod(pod_name)
