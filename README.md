#My code path exaplined

Basic flow using a particular algorithm

1.	Getting the metrics of all the worker nodes and using a particular algorithm ranking these worker nodes according to CPU and memory as our parameters.
2.	Now after getting the rank of nodes we can now check if the metrics of the top ranked node is more than the threshold value .
3.	If no then stop the further process and proceed to next cycle
4.	If the value is more than threshold then list of the pods  in that node and find out the pod which is taking most metric value (CPU +memory) and save the name of the pod and the name of containers in the pod ( I have ran applications with single container in them and migrating that container )
5.	Now  we migrate this pod from the top ranked node to the least ranked node as to reduce the total load on the node.
6.	We have used multiple algorithms such as Electre-3 , Vikor and Topsis to rank the nodes and we are performing migrations according to these ranking.
7.	We dynamically change the threshold required for migration by considering if the top ranked node metrics are more than threshold then we migrate and update our threshold values to the value of the top ranked over loaded node.
In our experiment we are randomly adding applications to the worker nodes and for every 45 seconds running our algorithm and checking the metrices

Also we are checking for two applications 
1)	Nginx , which is a stateless application
2)	Zookeeper , which is a stateful application

The folders have files which correspond to 
i.	Checktry    --  These files check the metrics of the top ranked node and if the metrics are more than the threshold , then we continue our process of checkpointing.
ii.	Copy_tar --  These files contain reading time it took to copy the checkpointed tar file into the newly created pod to migrate to.
iii.	Curl – time taken for checkpointing the pod of the overloaded node
iv.	Extract – the time taken for restoring the .tar file in new node ( for restoring )
v.	Finding – finding the no of pods in a worker node
vi.	Pods_ -- gives the no of pods in  worker node before and after migration
vii.	Restore_ -- Total time taken for restore
viii.	Startup_latency – time taken for the new pod to be running where we deploy our migrated application
ix. I have used Access pods for obtaining the file from the worker node to the master node in order to migrate, there are multiple available other methods to do the same.


Code to setup txt file contains the necessary commands to initialize the single Master multi node cluster in Kubernetes

There might be some code files which are required missing hence download all files from another branch "all_files"
Here the code files refer to the supporting files which i used for performing operations



