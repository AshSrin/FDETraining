# Exercise B — admin cosine retrieval (no access control)

Ground-truth ranking over all stored chunks. Lower cosine distance = more similar.

## How does a Kubernetes Deployment manage application replicas?

| Rank | Document | Chunk | Heading | Groups | Distance | Source |
|---|---|---|---|---|---|---|
| 1 | `APP-deployment` Deployments | 0 | Deployments | APPLICATION_ENGINEERING | 0.1717 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ |
| 2 | `APP-deployment` Deployments | 91 | Deployments > Writing a Deployment Spec > Replicas | APPLICATION_ENGINEERING | 0.1741 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ |
| 3 | `APP-replicaset` ReplicaSet | 34 | ReplicaSet > What's next | APPLICATION_ENGINEERING | 0.1944 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ |
| 4 | `APP-replicaset` ReplicaSet | 30 | ReplicaSet > Alternatives to ReplicaSet > Deployment (recommended) | APPLICATION_ENGINEERING | 0.2070 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ |
| 5 | `APP-replicaset` ReplicaSet | 3 | ReplicaSet > Example | APPLICATION_ENGINEERING | 0.2144 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ |

## What are PersistentVolumes and PersistentVolumeClaims?

| Rank | Document | Chunk | Heading | Groups | Distance | Source |
|---|---|---|---|---|---|---|
| 1 | `PLAT-persistent-volumes` Persistent Volumes | 70 | Persistent Volumes > PersistentVolumeClaims | PLATFORM_ENGINEERING | 0.1661 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ |
| 2 | `PLAT-persistent-volumes` Persistent Volumes | 1 | Persistent Volumes > Introduction | PLATFORM_ENGINEERING | 0.1761 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ |
| 3 | `APP-statefulset` StatefulSets | 17 | StatefulSets > Pod Identity > Stable Storage | APPLICATION_ENGINEERING | 0.1762 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ |
| 4 | `PLAT-persistent-volumes` Persistent Volumes | 3 | Persistent Volumes > Introduction | PLATFORM_ENGINEERING | 0.1797 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ |
| 5 | `PLAT-persistent-volumes` Persistent Volumes | 29 | Persistent Volumes > Lifecycle of a volume and claim > Reserving a PersistentVolume | PLATFORM_ENGINEERING | 0.1816 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ |

## What are recommended Kubernetes RBAC practices?

| Rank | Document | Chunk | Heading | Groups | Distance | Source |
|---|---|---|---|---|---|---|
| 1 | `SEC-rbac-good-practices` Role Based Access Control Good Practices | 0 | Role Based Access Control Good Practices | SECURITY_ENGINEERING | 0.1681 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ |
| 2 | `SEC-secrets-good-practices` Good practices for Kubernetes Secrets | 2 | Good practices for Kubernetes Secrets > Cluster administrators > Configure least-privilege access to Secrets | SECURITY_ENGINEERING | 0.2009 | https://kubernetes.io/docs/concepts/security/secrets-good-practices/ |
| 3 | `SEC-rbac-good-practices` Role Based Access Control Good Practices | 7 | Role Based Access Control Good Practices > General good practice > Hardening | SECURITY_ENGINEERING | 0.2104 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ |
| 4 | `SEC-rbac-good-practices` Role Based Access Control Good Practices | 18 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks > Access to `proxy` subresource of Nodes | SECURITY_ENGINEERING | 0.2137 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ |
| 5 | `SEC-rbac-good-practices` Role Based Access Control Good Practices | 9 | Role Based Access Control Good Practices > General good practice > Periodic review | SECURITY_ENGINEERING | 0.2158 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ |

## What are the main Kubernetes components?

| Rank | Document | Chunk | Heading | Groups | Distance | Source |
|---|---|---|---|---|---|---|
| 1 | `SHARED-components` Kubernetes Components | 0 | Kubernetes Components > Core Components | ALL_EMPLOYEES | 0.1534 | https://kubernetes.io/docs/concepts/overview/components/ |
| 2 | `SHARED-components` Kubernetes Components | 4 | Kubernetes Components > Flexibility in Architecture | ALL_EMPLOYEES | 0.1872 | https://kubernetes.io/docs/concepts/overview/components/ |
| 3 | `SHARED-components` Kubernetes Components | 1 | Kubernetes Components > Core Components > Control Plane Components | ALL_EMPLOYEES | 0.1966 | https://kubernetes.io/docs/concepts/overview/components/ |
| 4 | `SHARED-components` Kubernetes Components | 3 | Kubernetes Components > Addons | ALL_EMPLOYEES | 0.2016 | https://kubernetes.io/docs/concepts/overview/components/ |
| 5 | `SHARED-kubernetes-api` The Kubernetes API | 2 | The Kubernetes API | ALL_EMPLOYEES | 0.2146 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ |
