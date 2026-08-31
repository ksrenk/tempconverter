Docker Swarm and Kubernetes Comparison

Introduction

Two container orchestration platforms were evaluated for the TempConverter
application: Docker Swarm as the simpler orchestration platform and Kubernetes
(K3s) as the more complex orchestration platform.

Both deployments contained one MySQL database instance and multiple
TempConverter application replicas. The application was exposed externally
over HTTP port 80 and the application replicas were scheduled on different
cluster nodes.

Docker Swarm

Docker Swarm was simpler to configure and deploy. The cluster consisted of one
manager and multiple worker nodes running inside Multipass virtual machines.

The complete application was described in a Docker stack file. The MySQL
service used one replica, while TempConverter initially used two replicas.

The following placement configuration prevented multiple TempConverter
replicas from being scheduled on the same worker:

    max_replicas_per_node: 1

The application was exposed using Docker Swarm's ingress routing mesh:

    published: 80
    target: 5000
    mode: ingress

This allowed requests received on port 80 to be routed to the TempConverter
service.

Scaling was simple:

    docker service scale tempconverter_app=3

After adding a third worker, Swarm scheduled the three replicas on three
different worker nodes.

One issue encountered during deployment was database startup ordering.
TempConverter attempted to connect before MySQL was ready. The application
tasks failed temporarily, but the configured Swarm restart policy restarted
them until the database became available.

Kubernetes

Kubernetes required more configuration than Docker Swarm. The K3s cluster
contained one control-plane node and three worker nodes.

The deployment was divided into multiple Kubernetes resources:

- Namespace
- Secret
- MySQL Service
- MySQL StatefulSet
- PersistentVolumeClaim
- TempConverter Deployment
- TempConverter Service
- Ingress

The TempConverter Deployment initially used two replicas. Required pod
anti-affinity was used to prevent the application replicas from being placed
on the same Kubernetes node.

Kubernetes also provided more explicit mechanisms for application readiness.
An init container waited for the MySQL TCP port before TempConverter started,
and readiness probes were used to determine whether MySQL and TempConverter
were ready to receive traffic.

MySQL was deployed using a StatefulSet with persistent storage, which is more
appropriate for a stateful database workload than treating the database as a
normal stateless application.

The TempConverter application was exposed through a Kubernetes Service and
Traefik Ingress on HTTP port 80.

Scaling was performed using:

    kubectl scale deployment tempconverter --replicas=3 -n tempconverter

Because pod anti-affinity was configured, the three application pods were
scheduled on different Kubernetes nodes.

Comparison

Docker Swarm required considerably less configuration. A single stack file
was sufficient to describe the application, database, networking, replicas,
placement constraints and published port. Its commands were also simple and
closely related to normal Docker commands. This made Swarm quicker to learn
and appropriate for smaller deployments where simplicity is important.

Kubernetes required more resources and configuration files, but provided more
fine-grained control over the deployment. Features such as StatefulSets,
persistent volume claims, readiness probes, init containers, Services,
Ingress and pod anti-affinity made it possible to describe application
behaviour and availability in greater detail.

Both systems automatically scheduled containers across cluster nodes and both
supported horizontal scaling. Swarm used `max_replicas_per_node` to separate
replicas, while Kubernetes used pod anti-affinity rules.

Networking was also handled differently. Swarm used an overlay network and
its ingress routing mesh. Kubernetes separated networking into Services and
Ingress resources, with Traefik acting as the HTTP ingress controller.

The database startup problem demonstrated another difference. In the Swarm
deployment, failed application containers were recovered by the restart
policy. In Kubernetes, an init container was used to explicitly wait until
the database service was reachable before starting the application.

Conclusion

Docker Swarm was easier and faster to configure for the TempConverter project.
It required fewer configuration objects and provided a straightforward method
for deploying and scaling a small multi-node application.

Kubernetes had a steeper learning curve and required more configuration, but
provided stronger mechanisms for scheduling, health checking, persistent
storage, service discovery and application lifecycle management.

For a small application or educational environment, Docker Swarm provides a
simple orchestration solution. For larger systems requiring more sophisticated
availability, scheduling, networking and state management, Kubernetes provides
greater flexibility and control.
