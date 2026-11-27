# Exercise D — same question, different results

Tenant `TECHORG_ENGINEERING` · top-5 by cosine distance (lower = closer) · user results come from `search.py` (restricted reader role, PostgreSQL RLS).

| User | Groups |
|---|---|
| Priya | ALL_EMPLOYEES, APPLICATION_ENGINEERING |
| Arjun | ALL_EMPLOYEES, PLATFORM_ENGINEERING |
| Meena | ALL_EMPLOYEES, SECURITY_ENGINEERING |
| Divya | ALL_EMPLOYEES, APPLICATION_ENGINEERING, SECURITY_ENGINEERING |

**Result: 80 results returned to users, 0 unauthorized.**

## Summary — top-1 result per user

| Question | Area | Priya | Arjun | Meena | Divya |
|---|---|---|---|---|---|
| How does a Kubernetes Deployment manage application replicas? | Application Engineering | `APP-deployment` 0.1718 | `SHARED-kubernetes-api` 0.251 | `SHARED-kubernetes-api` 0.251 | `APP-deployment` 0.1718 |
| What are PersistentVolumes and PersistentVolumeClaims? | Platform Engineering | `APP-statefulset` 0.1762 | `PLAT-persistent-volumes` 0.1661 | `SEC-rbac-good-practices` 0.2195 | `APP-statefulset` 0.1762 |
| What are recommended Kubernetes RBAC practices? | Security Engineering | `SHARED-kubernetes-api` 0.2788 | `PLAT-storage-classes` 0.2764 | `SEC-rbac-good-practices` 0.1681 | `SEC-rbac-good-practices` 0.1681 |
| What are the main Kubernetes components? | Shared knowledge | `SHARED-components` 0.1534 | `SHARED-components` 0.1534 | `SHARED-components` 0.1534 | `SHARED-components` 0.1534 |

## After the relevance cutoff (cosine distance <= 0.23)

Chunks that would be passed to an answer generator. Raw top-k above is the evidence; when 0 chunks pass, the user gets: *"No relevant information found in the documents you have access to."* (same message whether the relevant content is restricted or absent).

| Question | Priya | Arjun | Meena | Divya |
|---|---|---|---|---|
| How does a Kubernetes Deployment manage application replicas? | 5/5 | no answer | no answer | 5/5 |
| What are PersistentVolumes and PersistentVolumeClaims? | 2/5 | 5/5 | 1/5 | 3/5 |
| What are recommended Kubernetes RBAC practices? | no answer | no answer | 5/5 | 5/5 |
| What are the main Kubernetes components? | 5/5 | 5/5 | 5/5 | 5/5 |

## How does a Kubernetes Deployment manage application replicas?

Primary knowledge area: **Application Engineering**

### Ground truth (admin, no access control)

| Rank | Document | Heading | Groups | Distance | Priya | Arjun | Meena | Divya |
|---|---|---|---|---|---|---|---|---|
| 1 | [`APP-deployment`](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) #0 | Deployments | APPLICATION_ENGINEERING | 0.1718 | ✅ | ⛔ | ⛔ | ✅ |
| 2 | [`APP-deployment`](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) #91 | Deployments > Writing a Deployment Spec > Replicas | APPLICATION_ENGINEERING | 0.1742 | ✅ | ⛔ | ⛔ | ✅ |
| 3 | [`APP-replicaset`](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) #34 | ReplicaSet > What's next | APPLICATION_ENGINEERING | 0.1945 | ✅ | ⛔ | ⛔ | ✅ |
| 4 | [`APP-replicaset`](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) #30 | ReplicaSet > Alternatives to ReplicaSet > Deployment (recommended) | APPLICATION_ENGINEERING | 0.2071 | ✅ | ⛔ | ⛔ | ✅ |
| 5 | [`APP-replicaset`](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) #3 | ReplicaSet > Example | APPLICATION_ENGINEERING | 0.2144 | ✅ | ⛔ | ⛔ | ✅ |

### Priya (ALL_EMPLOYEES, APPLICATION_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `APP-deployment` #0 | Deployments | 0.1718 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | ✅ | kept |
| 2 | `APP-deployment` #91 | Deployments > Writing a Deployment Spec > Replicas | 0.1742 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | ✅ | kept |
| 3 | `APP-replicaset` #34 | ReplicaSet > What's next | 0.1945 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ | ✅ | kept |
| 4 | `APP-replicaset` #30 | ReplicaSet > Alternatives to ReplicaSet > Deployment (recommended) | 0.2071 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ | ✅ | kept |
| 5 | `APP-replicaset` #3 | ReplicaSet > Example | 0.2144 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ | ✅ | kept |

### Arjun (ALL_EMPLOYEES, PLATFORM_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `SHARED-kubernetes-api` #23 | The Kubernetes API > API groups and versioning | 0.251 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |
| 2 | `SHARED-kubernetes-api` #26 | The Kubernetes API > API groups and versioning > API changes | 0.2563 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |
| 3 | `PLAT-persistent-volumes` #6 | Persistent Volumes > Lifecycle of a volume and claim > Provisioning > Static | 0.2636 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | ✅ | dropped |
| 4 | `PLAT-persistent-volumes` #37 | Persistent Volumes > Lifecycle of a volume and claim > Expanding Persistent Volumes Claims > Resizing an in-use PersistentVolumeClaim | 0.2693 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | ✅ | dropped |
| 5 | `SHARED-kubernetes-api` #27 | The Kubernetes API > API groups and versioning > API changes | 0.2704 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |

### Meena (ALL_EMPLOYEES, SECURITY_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `SHARED-kubernetes-api` #23 | The Kubernetes API > API groups and versioning | 0.251 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |
| 2 | `SHARED-kubernetes-api` #26 | The Kubernetes API > API groups and versioning > API changes | 0.2563 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |
| 3 | `SHARED-kubernetes-api` #27 | The Kubernetes API > API groups and versioning > API changes | 0.2704 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |
| 4 | `SHARED-kubectl` #3 | The kubectl command-line tool > How kubectl works | 0.2743 | https://kubernetes.io/docs/concepts/overview/kubectl/ | ✅ | dropped |
| 5 | `SHARED-kubernetes-api` #2 | The Kubernetes API | 0.2744 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |

### Divya (ALL_EMPLOYEES, APPLICATION_ENGINEERING, SECURITY_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `APP-deployment` #0 | Deployments | 0.1718 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | ✅ | kept |
| 2 | `APP-deployment` #91 | Deployments > Writing a Deployment Spec > Replicas | 0.1742 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | ✅ | kept |
| 3 | `APP-replicaset` #34 | ReplicaSet > What's next | 0.1945 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ | ✅ | kept |
| 4 | `APP-replicaset` #30 | ReplicaSet > Alternatives to ReplicaSet > Deployment (recommended) | 0.2071 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ | ✅ | kept |
| 5 | `APP-replicaset` #3 | ReplicaSet > Example | 0.2144 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ | ✅ | kept |

## What are PersistentVolumes and PersistentVolumeClaims?

Primary knowledge area: **Platform Engineering**

### Ground truth (admin, no access control)

| Rank | Document | Heading | Groups | Distance | Priya | Arjun | Meena | Divya |
|---|---|---|---|---|---|---|---|---|
| 1 | [`PLAT-persistent-volumes`](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) #70 | Persistent Volumes > PersistentVolumeClaims | PLATFORM_ENGINEERING | 0.1661 | ⛔ | ✅ | ⛔ | ⛔ |
| 2 | [`PLAT-persistent-volumes`](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) #1 | Persistent Volumes > Introduction | PLATFORM_ENGINEERING | 0.1761 | ⛔ | ✅ | ⛔ | ⛔ |
| 3 | [`APP-statefulset`](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) #17 | StatefulSets > Pod Identity > Stable Storage | APPLICATION_ENGINEERING | 0.1762 | ✅ | ⛔ | ⛔ | ✅ |
| 4 | [`PLAT-persistent-volumes`](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) #3 | Persistent Volumes > Introduction | PLATFORM_ENGINEERING | 0.1797 | ⛔ | ✅ | ⛔ | ⛔ |
| 5 | [`PLAT-persistent-volumes`](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) #29 | Persistent Volumes > Lifecycle of a volume and claim > Reserving a PersistentVolume | PLATFORM_ENGINEERING | 0.1816 | ⛔ | ✅ | ⛔ | ⛔ |

### Priya (ALL_EMPLOYEES, APPLICATION_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `APP-statefulset` #17 | StatefulSets > Pod Identity > Stable Storage | 0.1762 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | ✅ | kept |
| 2 | `APP-statefulset` #7 | StatefulSets > Components > Volume Claim Templates | 0.2194 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | ✅ | kept |
| 3 | `APP-statefulset` #42 | StatefulSets > PersistentVolumeClaim retention | 0.2386 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | ✅ | dropped |
| 4 | `APP-statefulset` #44 | StatefulSets > PersistentVolumeClaim retention | 0.2419 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | ✅ | dropped |
| 5 | `APP-statefulset` #45 | StatefulSets > PersistentVolumeClaim retention | 0.2492 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | ✅ | dropped |

### Arjun (ALL_EMPLOYEES, PLATFORM_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `PLAT-persistent-volumes` #70 | Persistent Volumes > PersistentVolumeClaims | 0.1661 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | ✅ | kept |
| 2 | `PLAT-persistent-volumes` #1 | Persistent Volumes > Introduction | 0.1761 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | ✅ | kept |
| 3 | `PLAT-persistent-volumes` #3 | Persistent Volumes > Introduction | 0.1797 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | ✅ | kept |
| 4 | `PLAT-persistent-volumes` #29 | Persistent Volumes > Lifecycle of a volume and claim > Reserving a PersistentVolume | 0.1816 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | ✅ | kept |
| 5 | `PLAT-volume-snapshots` #10 | Volume Snapshots > Lifecycle of a volume snapshot and volume snapshot content > Persistent Volume Claim as Snapshot Source Protection | 0.1869 | https://kubernetes.io/docs/concepts/storage/volume-snapshots/ | ✅ | kept |

### Meena (ALL_EMPLOYEES, SECURITY_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `SEC-rbac-good-practices` #16 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks > Persistent volume creation | 0.2195 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | kept |
| 2 | `SEC-rbac-good-practices` #15 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks > Persistent volume creation | 0.2727 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | dropped |
| 3 | `SEC-security-checklist` #39 | Security Checklist > Admission controllers | 0.3326 | https://kubernetes.io/docs/concepts/security/security-checklist/ | ✅ | dropped |
| 4 | `SEC-pod-security-standards` #25 | Pod Security Standards > Profile Details > Restricted | 0.3415 | https://kubernetes.io/docs/concepts/security/pod-security-standards/ | ✅ | dropped |
| 5 | `SEC-security-checklist` #24 | Security Checklist > Secrets | 0.354 | https://kubernetes.io/docs/concepts/security/security-checklist/ | ✅ | dropped |

### Divya (ALL_EMPLOYEES, APPLICATION_ENGINEERING, SECURITY_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `APP-statefulset` #17 | StatefulSets > Pod Identity > Stable Storage | 0.1762 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | ✅ | kept |
| 2 | `APP-statefulset` #7 | StatefulSets > Components > Volume Claim Templates | 0.2194 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | ✅ | kept |
| 3 | `SEC-rbac-good-practices` #16 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks > Persistent volume creation | 0.2195 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | kept |
| 4 | `APP-statefulset` #42 | StatefulSets > PersistentVolumeClaim retention | 0.2386 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | ✅ | dropped |
| 5 | `APP-statefulset` #44 | StatefulSets > PersistentVolumeClaim retention | 0.2419 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | ✅ | dropped |

## What are recommended Kubernetes RBAC practices?

Primary knowledge area: **Security Engineering**

### Ground truth (admin, no access control)

| Rank | Document | Heading | Groups | Distance | Priya | Arjun | Meena | Divya |
|---|---|---|---|---|---|---|---|---|
| 1 | [`SEC-rbac-good-practices`](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) #0 | Role Based Access Control Good Practices | SECURITY_ENGINEERING | 0.1681 | ⛔ | ⛔ | ✅ | ✅ |
| 2 | [`SEC-secrets-good-practices`](https://kubernetes.io/docs/concepts/security/secrets-good-practices/) #2 | Good practices for Kubernetes Secrets > Cluster administrators > Configure least-privilege access to Secrets | SECURITY_ENGINEERING | 0.2009 | ⛔ | ⛔ | ✅ | ✅ |
| 3 | [`SEC-rbac-good-practices`](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) #7 | Role Based Access Control Good Practices > General good practice > Hardening | SECURITY_ENGINEERING | 0.2104 | ⛔ | ⛔ | ✅ | ✅ |
| 4 | [`SEC-rbac-good-practices`](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) #18 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks > Access to `proxy` subresource of Nodes | SECURITY_ENGINEERING | 0.2138 | ⛔ | ⛔ | ✅ | ✅ |
| 5 | [`SEC-rbac-good-practices`](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) #9 | Role Based Access Control Good Practices > General good practice > Periodic review | SECURITY_ENGINEERING | 0.2158 | ⛔ | ⛔ | ✅ | ✅ |

### Priya (ALL_EMPLOYEES, APPLICATION_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `SHARED-kubernetes-api` #2 | The Kubernetes API | 0.2788 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |
| 2 | `SHARED-kubernetes-api` #23 | The Kubernetes API > API groups and versioning | 0.2799 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |
| 3 | `SHARED-components` #3 | Kubernetes Components > Addons | 0.2872 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | dropped |
| 4 | `SHARED-components` #1 | Kubernetes Components > Core Components > Control Plane Components | 0.2878 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | dropped |
| 5 | `SHARED-kubectl` #10 | The kubectl command-line tool > What's next | 0.2925 | https://kubernetes.io/docs/concepts/overview/kubectl/ | ✅ | dropped |

### Arjun (ALL_EMPLOYEES, PLATFORM_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `PLAT-storage-classes` #35 | Storage Classes > Parameters > Ceph RBD (deprecated) | 0.2764 | https://kubernetes.io/docs/concepts/storage/storage-classes/ | ✅ | dropped |
| 2 | `SHARED-kubernetes-api` #2 | The Kubernetes API | 0.2788 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |
| 3 | `SHARED-kubernetes-api` #23 | The Kubernetes API > API groups and versioning | 0.2799 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | dropped |
| 4 | `SHARED-components` #3 | Kubernetes Components > Addons | 0.2872 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | dropped |
| 5 | `SHARED-components` #1 | Kubernetes Components > Core Components > Control Plane Components | 0.2878 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | dropped |

### Meena (ALL_EMPLOYEES, SECURITY_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `SEC-rbac-good-practices` #0 | Role Based Access Control Good Practices | 0.1681 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | kept |
| 2 | `SEC-secrets-good-practices` #2 | Good practices for Kubernetes Secrets > Cluster administrators > Configure least-privilege access to Secrets | 0.2009 | https://kubernetes.io/docs/concepts/security/secrets-good-practices/ | ✅ | kept |
| 3 | `SEC-rbac-good-practices` #7 | Role Based Access Control Good Practices > General good practice > Hardening | 0.2104 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | kept |
| 4 | `SEC-rbac-good-practices` #18 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks > Access to `proxy` subresource of Nodes | 0.2138 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | kept |
| 5 | `SEC-rbac-good-practices` #9 | Role Based Access Control Good Practices > General good practice > Periodic review | 0.2158 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | kept |

### Divya (ALL_EMPLOYEES, APPLICATION_ENGINEERING, SECURITY_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `SEC-rbac-good-practices` #0 | Role Based Access Control Good Practices | 0.1681 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | kept |
| 2 | `SEC-secrets-good-practices` #2 | Good practices for Kubernetes Secrets > Cluster administrators > Configure least-privilege access to Secrets | 0.2009 | https://kubernetes.io/docs/concepts/security/secrets-good-practices/ | ✅ | kept |
| 3 | `SEC-rbac-good-practices` #7 | Role Based Access Control Good Practices > General good practice > Hardening | 0.2104 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | kept |
| 4 | `SEC-rbac-good-practices` #18 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks > Access to `proxy` subresource of Nodes | 0.2138 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | kept |
| 5 | `SEC-rbac-good-practices` #9 | Role Based Access Control Good Practices > General good practice > Periodic review | 0.2158 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | ✅ | kept |

## What are the main Kubernetes components?

Primary knowledge area: **Shared knowledge**

### Ground truth (admin, no access control)

| Rank | Document | Heading | Groups | Distance | Priya | Arjun | Meena | Divya |
|---|---|---|---|---|---|---|---|---|
| 1 | [`SHARED-components`](https://kubernetes.io/docs/concepts/overview/components/) #0 | Kubernetes Components > Core Components | ALL_EMPLOYEES | 0.1534 | ✅ | ✅ | ✅ | ✅ |
| 2 | [`SHARED-components`](https://kubernetes.io/docs/concepts/overview/components/) #4 | Kubernetes Components > Flexibility in Architecture | ALL_EMPLOYEES | 0.1872 | ✅ | ✅ | ✅ | ✅ |
| 3 | [`SHARED-components`](https://kubernetes.io/docs/concepts/overview/components/) #1 | Kubernetes Components > Core Components > Control Plane Components | ALL_EMPLOYEES | 0.1966 | ✅ | ✅ | ✅ | ✅ |
| 4 | [`SHARED-components`](https://kubernetes.io/docs/concepts/overview/components/) #3 | Kubernetes Components > Addons | ALL_EMPLOYEES | 0.2016 | ✅ | ✅ | ✅ | ✅ |
| 5 | [`SHARED-kubernetes-api`](https://kubernetes.io/docs/concepts/overview/kubernetes-api/) #2 | The Kubernetes API | ALL_EMPLOYEES | 0.2146 | ✅ | ✅ | ✅ | ✅ |

### Priya (ALL_EMPLOYEES, APPLICATION_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `SHARED-components` #0 | Kubernetes Components > Core Components | 0.1534 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 2 | `SHARED-components` #4 | Kubernetes Components > Flexibility in Architecture | 0.1872 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 3 | `SHARED-components` #1 | Kubernetes Components > Core Components > Control Plane Components | 0.1966 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 4 | `SHARED-components` #3 | Kubernetes Components > Addons | 0.2016 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 5 | `SHARED-kubernetes-api` #2 | The Kubernetes API | 0.2146 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | kept |

### Arjun (ALL_EMPLOYEES, PLATFORM_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `SHARED-components` #0 | Kubernetes Components > Core Components | 0.1534 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 2 | `SHARED-components` #4 | Kubernetes Components > Flexibility in Architecture | 0.1872 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 3 | `SHARED-components` #1 | Kubernetes Components > Core Components > Control Plane Components | 0.1966 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 4 | `SHARED-components` #3 | Kubernetes Components > Addons | 0.2016 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 5 | `SHARED-kubernetes-api` #2 | The Kubernetes API | 0.2146 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | kept |

### Meena (ALL_EMPLOYEES, SECURITY_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `SHARED-components` #0 | Kubernetes Components > Core Components | 0.1534 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 2 | `SHARED-components` #4 | Kubernetes Components > Flexibility in Architecture | 0.1872 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 3 | `SHARED-components` #1 | Kubernetes Components > Core Components > Control Plane Components | 0.1966 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 4 | `SHARED-components` #3 | Kubernetes Components > Addons | 0.2016 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 5 | `SHARED-kubernetes-api` #2 | The Kubernetes API | 0.2146 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | kept |

### Divya (ALL_EMPLOYEES, APPLICATION_ENGINEERING, SECURITY_ENGINEERING)

| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |
|---|---|---|---|---|---|---|
| 1 | `SHARED-components` #0 | Kubernetes Components > Core Components | 0.1534 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 2 | `SHARED-components` #4 | Kubernetes Components > Flexibility in Architecture | 0.1872 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 3 | `SHARED-components` #1 | Kubernetes Components > Core Components > Control Plane Components | 0.1966 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 4 | `SHARED-components` #3 | Kubernetes Components > Addons | 0.2016 | https://kubernetes.io/docs/concepts/overview/components/ | ✅ | kept |
| 5 | `SHARED-kubernetes-api` #2 | The Kubernetes API | 0.2146 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | ✅ | kept |
