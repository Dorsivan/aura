## Gitaly On Kubernetes

Gitaly cannot be deployed on Kubernetes in an HA manner. What you have to do is actually deploy it as a Gitaly Cluster.

## Migrating for Gitaly on Kubernetes to Cluster

In case you want to move all of the data from a single pod to a cluster, or just generally between clusters (Why? you can easily swap the nodes, and they have to remain in the same versions anyways)

The guide is helpful, but

You should remember:
1. Moving causes no real disruption in GitLab, it might cause a certain repository to be unavailable for a couple of moments. No need for downtime.
2. If trying to move from Kubernetes, you need a way to expose the service to the outside world, since the gitaly cluster will attempt to communicate with it. You can create a LoadBalancer service, and make gitlab communicate with gitaly through it, rather than the internal address