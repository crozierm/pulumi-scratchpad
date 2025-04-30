import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.core.v1 import Namespace

def create_ubuntu_container(namespace: Namespace):

    ubuntu_deployment = k8s.apps.v1.Deployment(
        "ubuntu-deployment",
        opts=pulumi.ResourceOptions(depends_on=[namespace]),
        metadata={
            "namespace": namespace.metadata["name"],
        },
        spec={
            "selector": {
                "matchLabels": {"app": "ubuntu"},
            },
            "replicas": 1,  # Single Ubuntu host
            "template": {
                "metadata": {
                    "labels": {"app": "ubuntu"},
                },
                "spec": {
                    "containers": [
                        {
                            "name": "ubuntu-container",
                            "image": "ubuntu:24.04",  # Use Ubuntu 20.04 container image
                            "resources": {
                                "requests": {
                                    "cpu": "500m",
                                    "memory": "512Mi",
                                },
                                "limits": {
                                    "cpu": "1",
                                    "memory": "1Gi",
                                },
                            },
                            "ports": [
                                {"containerPort": 22},  # SSH port exposed in the container
                            ],
                            "command": ["/bin/bash", "-c", "--"],  # Start with bash for debugging
                            "args": [
                                "tail -f /dev/null"
                            ],
                        }
                    ],
                },
            },
        },
    )

