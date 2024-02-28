#!/bin/bash

while true
do
    sudo systemctl daemon-reload
    sudo systemctl restart kubelet
    mkdir -p $HOME/.kube
    sudo cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    export KUBECONFIG=/etc/kubernetes/admin.conf

    kubectl apply -f components.yaml

    sleep 45  # Adjust the sleep duration as needed
done
