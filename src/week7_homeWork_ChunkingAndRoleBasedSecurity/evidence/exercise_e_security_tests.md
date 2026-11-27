# Exercise E — negative tests and revocation

Run 2026-11-27 11:05:27 · tenant `TECHORG_ENGINEERING` · restricted document `SEC-rbac-good-practices` · question *What are recommended Kubernetes RBAC practices?*

All retrieval runs as `k8s_rag_reader` under PostgreSQL RLS. Full transcript: `exercise_e_security_tests.txt`.

| ID | Check | Result | Evidence |
|---|---|---|---|
| E1 | Meena (SECURITY_ENGINEERING) retrieves restricted SEC-rbac-good-practices | ✅ PASS | top results: SEC-rbac-good-practices#0 d=0.1681, SEC-secrets-good-practices#2 d=0.2009, SEC-rbac-good-practices#7 d=0.2104; 29 chunks of SEC-rbac-good-practices visible |
| E2 | Arjun cannot retrieve SEC-rbac-good-practices (not in SECURITY_ENGINEERING) | ✅ PASS | SEC-rbac-good-practices in top-20: 0; direct chunk count: 0; document row visible: False; best they get instead: PLAT-storage-classes#35 d=0.2764 |
| E2 | Priya cannot retrieve SEC-rbac-good-practices (not in SECURITY_ENGINEERING) | ✅ PASS | SEC-rbac-good-practices in top-20: 0; direct chunk count: 0; document row visible: False; best they get instead: SHARED-kubernetes-api#2 d=0.2788 |
| E3 | Revoking SECURITY_ENGINEERING removes Meena's access on the very next query | ✅ PASS | SEC-rbac-good-practices chunks visible: 29 -> 0 (next query, 15 ms); SEC-* documents visible: 0; top results now: SHARED-kubernetes-api#2 d=0.2788, SHARED-kubernetes-api#23 d=0.2799, SHARED-components#3 d=0.2872 |
| E3 | Revocation needed no re-embedding or re-ingesting | ✅ PASS | chunk count, max chunk_id and embedding hash identical before/after revoke |
| E3 | Revocation is scoped: Meena keeps ALL_EMPLOYEES shared documents | ✅ PASS | SHARED-* documents still visible: 5 |
| E5 | Restoring SECURITY_ENGINEERING returns Meena's authorized access | ✅ PASS | SEC-rbac-good-practices chunks visible: 29; top results: SEC-rbac-good-practices#0 d=0.1681, SEC-secrets-good-practices#2 d=0.2009, SEC-rbac-good-practices#7 d=0.2104 (identical to E1: True) |
| E4 | Unknown identity 'intruder' cannot read protected chunks | ✅ PASS | chunks visible: 0; SEC-rbac-good-practices chunks: 0; documents visible: 0 |
| E4 | Look-alike identity 'Meena ' (capital + trailing space) is unknown to the database | ✅ PASS | chunks visible: 0 |
| E4 | Unknown identity 'admin' cannot read protected chunks | ✅ PASS | chunks visible: 0; SEC-rbac-good-practices chunks: 0; documents visible: 0 |
| E4 | search.py path: unknown identity gets zero results | ✅ PASS | results returned: 0 |
| X1 | No identity set at all -> fail closed | ✅ PASS | chunks visible: 0 |
| X2 | Valid user with the wrong tenant (OTHER_ORG) sees nothing | ✅ PASS | SEC-rbac-good-practices chunks visible: 0 |
| X3 | Divya (APP + SECURITY) reads both departments + shared, but not Platform | ✅ PASS | APP=10 SEC=5 SHARED=5 PLAT=0 |
| X4 | Reader cannot read the ACL table | ✅ PASS | InsufficientPrivilege: permission denied for table document_acl |
| X4 | Reader cannot read identity tables | ✅ PASS | InsufficientPrivilege: permission denied for table user_groups |
| X5 | Reader cannot grant itself a group | ✅ PASS | InsufficientPrivilege: permission denied for table user_groups |
| X5 | Reader cannot modify stored chunks | ✅ PASS | InsufficientPrivilege: permission denied for table chunks |
| X6 | Reader cannot switch RLS off (SET row_security = off) | ✅ PASS | InsufficientPrivilege: query would be affected by row-level security policy for table "chunks" |
