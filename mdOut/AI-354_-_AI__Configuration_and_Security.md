---
title: "AI-354 - AI+ Configuration and Security"
source_file: "AI-354_-_AI__Configuration_and_Security.doc"
converted_date: "2025-09-17T11:24:58.983189"
format: "markdown"
---

# AI-354 - AI+ Configuration and Security

This guide provides a comprehensive overview of setting up HashiCorp Vau=lt and Consul for AI+, with a focus on deployment in containerized environm=ents. It covers both standalone and clustered deployments, and consideratio=ns for future Kubernetes integration. While this guide focuses on container=ized deployments, the principles apply to non-containerized environments as= well.

> **Important** : This guide assumes that TLS is used for all =communication between Vault and Consul, even in non-clustered, air-gapped e=nvironments. Mutual TLS \(mTLS\) will be used where applicable.

## # Vault

Vault is a tool for securely managing secrets. It provides a unified int=erface to any secret, tight access control, and record logging. In this set=up, we'll use Consul as the storage backend for Vault.

## # Consul

Consul is a service mesh solution providing a full-featured control plan=e with service discovery, configuration, and orchestration capabilities. In= this guide, Consul is used as a highly available, distributed key-value st=ore for Vault.

# # Certifi�te Generation

For TLS encryption, you'll need to generate:

1. A Certificate Authority \(CA\) certificate

2. Server certificates for Vault and Consul

3. Client certificates for mTLS authentication

Here's a brief example using OpenSSL:

# Creat=e a CAopenssl genrsa -out ca.key 4096openssl req -new -x509 -key ca.key -sha256 -subj "/CN=vault-ca" -out ca.c=rt# Create certificates for Consulopenssl genrsa -out consul.key 2048openssl req -new -key consul.key -out consul.csr -subj "/CN=consul"openssl x509 -req -in consul.csr -CA ca.crt -CAkey ca.key -CAcreateserial -=out consul.crt# Create certificates for Vaultopenssl genrsa -out vault.key 2048openssl req -new -key vault.key -out vault.csr -subj "/CN=vault"openssl x509 -req -in vault.csr -CA ca.crt -CAkey ca.key -CAcreateserial -o=ut vault.crt

# # Vault Setup

## # Pre-Conditions=

- Vault is deployed in a containerized environment using Docker Compose

- Vault is initialized using Shamir Secret Sharing, with unseal keys distr=ibuted manually

- Environment variables \(e.g., `VAULT_DEV_ROOT_TOKEN_ID`\) are s=et via `.env` files or securely passed into containers

- Persistent storage is mounted from the host filesystem

- Vault uses Consul as a storage backend

- TLS is enabled for all communication

## # Configu=ration Overview

- **Storage backend** : Consul

- **Listener** : TCP with TLS enabled

- **Vault UI** : Enabled

- **Initialization** : Manual \(`vault operator init)`

- **Unsealing** : Manual \(`vault operator unseal`\),= using Shamir Secret Sharing \(e.g., 5 key shares, 3 threshold\)

- **Root token handling** : Manual \(secure distribution offlin=e\)

- **Configuration** : Provided via the `VAULT_LOCAL_CONFI=G` environment variable

# # Standalo=ne Deployment

## # Vault Configuration \(Standalone\)

storage= "consul" { address = "https://consul:8500" # Consul address, include port path = "vault/" # Path in Consul KV tls_ca_file = "/vault/certs/ca.crt" tls_cert_file = "/vault/certs/vault.crt" tls_key_file = "/vault/certs/vault.key"}listener "tcp" { address = "0.0.0.0:8200" tls_cert_file = "/vault/certs/vault.crt" tls_key_file = "/vault/certs/vault.key" client_cert_auth = "require" # Require client certificates}ui = true

- **tls\_ca\_file** : Path to the CA certificate

- **tls\_cert\_file** : Path to the Vault server certificate

=
- **tls\_key\_file** : Path to the Vault server private key

<=/li>
- **client\_cert\_auth** : Set to "require" to enable mTLS

## # Initialization & Unseal Process \(Standalone\)

1. Start Consul

2. Start Vault

3. Execute a shell within the Vault container:

docker =exec -it vault sh

4. Initialize Vault:

vault o=perator init -key-shares=5 -key-threshold=3

5. Securely store the output, which includes:

- 5 unseal keys

- 1 root token

**Important** : These keys are non-recoverable. DO NOT LOSE =THEM\!

6. Unseal Vault with any 3 of the 5 unseal keys:

vault o=perator unseal -tls -address=https://0.0.0.0:8200 <key1>vault operator unseal -tls -address=https://0.0.0.0:8200 <key2>vault operator unseal -tls -address=https://0.0.0.0:8200 <key3>

7. Vault becomes available after unsealing

# # Clustered= Deployment

## # Vault Configuration \(Clustered\)

storage= "consul" { address = "https://consul1:8500,https://consul2:8500,https://consu=l3:8500" # Comma-separated list of Consul addresses path = "vault/" tls_ca_file = "/vault/certs/ca.crt" tls_cert_file = "/vault/certs/vault.crt" tls_key_file = "/vault/certs/vault.key"}listener "tcp" { address = "0.0.0.0:8200" tls_cert_file = "/vault/certs/vault.crt" tls_key_file = "/vault/certs/vault.key" client_cert_auth = "require"}cluster_name = "vault-cluster"ui = true

- **address** : Comma-separated list of Consul servers

- **cluster\_name** : The name of the Vault cluster

## # Initialization and Unseal Process \(Clustered\)

1. Start Consul cluster \(3 or 5 servers\)

2. Start Vault instances \(at least 3 for HA\)

3. Initialize only one Vault instance:

docker =exec -it vault-node-1 shvault operator init -key-shares=5 -key-threshold=3

4. Securely store the unseal keys and root token

5. Unseal the same Vault instance that was initialized:

vault o=perator unseal -tls -address=https://vault-node-1:8200 <key1>vault operator unseal -tls -address=https://vault-node-1:8200 <key2>=;vault operator unseal -tls -address=https://vault-node-1:8200 <key3>=;

6. Join the other Vault instances to the cluster after the first node is un=sealed:

On vault-node-2:

vault o=perator join -address=https://vault-node-1:8200 -tls

On vault-node-3:

vault o=perator join -address=https://vault-node-1:8200 -tls

7. Unseal the other Vault instances, one at a time, using keys from the ini=tial unseal process:

On vault-node-2:

vault o=perator unseal -tls -address=https://vault-node-2:8200 <key1>vault operator unseal -tls -address=https://vault-node-2:8200 <key2>=;vault operator unseal -tls -address=https://vault-node-2:8200 <key3>=;

On vault-node-3:

vault o=perator unseal -tls -address=https://vault-node-3:8200 <key1>vault operator unseal -tls -address=https://vault-node-3:8200 <key2>=;vault operator unseal -tls -address=https://vault-node-3:8200 <key3>=;

8. Vault cluster is available after all nodes are unsealed

# # Consul Setup

## # Pre-Conditio=ns

- Consul is deployed using Docker Compose

- TLS is enabled for all communication

- Consul is used to provide distributed configuration and store Vault data=

## # Confi=guration Overview

- **Mode** : Server \(standalone or clustered\)

- **DNS** : Disabled

- **Client mode** : Disabled

- **UI** : Enabled

- **Storage** : Local disk

- **TLS** : Enabled

## # Consul Configuration \(Standalone\)

server =3D truebootstrap_expect = 1ui = trueclient_addr = "0.0.0.0"bind_addr = "0.0.0.0"datacenter = "dc1"tls { enabled = true cert_file = "/consul/certs/consul.crt" key_file = "/consul/certs/consul.key" ca_file = "/consul/certs/ca.crt" verify_incoming = true verify_outgoing = true}

## # Consul Configuration \(Clustered\)

server =3D truebootstrap_expect = 3 # or 5ui = trueclient_addr = "0.0.0.0"bind_addr = "0.0.0.0"datacenter = "dc1"tls { enabled = true cert_file = "/consul/certs/consul.crt" key_file = "/consul/certs/consul.key" ca_file = "/consul/certs/ca.crt" verify_incoming = true verify_outgoing = true}retry_join = ["consul1", "consul2", "consul3"] # For each server

- **retry\_join** : Used to join the other Consul servers. Use =the private IPs or container names of the other Consul nodes.

# # Docker Com=pose Setup

A basic `docker-compose.yml` file orchestrates the Vault and =Consul services. All volumes are mapped locally, and networking is confined= to a dedicated Docker network.

version=: '3.8'services: consul: image: hashicorp/consul:1.15 container_name: consul restart: unless-stopped ports: - "8500:8500" - "8600:8600/udp" command: agent -server -bootstrap-expect=1 -ui -client=0.0.0.0 -bin=d=0.0.0.0 -data-dir=/consul/data -hcl='tls { enabled = true; cert_f=ile = "/consul/certs/consul.crt"; key_file = "/consul/certs/consul.key"=; ca_file = "/consul/certs/ca.crt"; verify_incoming = true; verify_outg=oing = true }' volumes: - ./consul/data:/consul/data - ./certs:/consul/certs # Mount certs networks: - vault-consul # Define a network consul2: # For Consul Cluster image: hashicorp/consul:1.15 container_name: consul2 restart: unless-stopped ports: - "8502:8500" - "8602:8600/udp" command: agent -server -retry-join="consul:8500" -ui -client=0.0.0.=0 -bind=0.0.0.0 -data-dir=/consul/data -hcl='tls { enabled = true; �rt_file = "/consul/certs/consul.crt"; key_file = "/consul/certs/consu=l.key"; ca_file = "/consul/certs/ca.crt"; verify_incoming = true; verif=y_outgoing = true }' volumes: - ./consul/data2:/consul/data - ./certs:/consul/certs networks: - vault-consul consul3: # For Consul Cluster image: hashicorp/consul:1.15 container_name: consul3 restart: unless-stopped ports: - "8503:8500" - "8603:8600/udp" command: agent -server -retry-join="consul:8500" -retry-join="consu=l2:8502" -ui -client=0.0.0.0 -bind=0.0.0.0 -data-dir=/consul/data -hc=l='tls { enabled = true; cert_file = "/consul/certs/consul.crt"; key_=file = "/consul/certs/consul.key"; ca_file = "/consul/certs/ca.crt"; ve=rify_incoming = true; verify_outgoing = true }' volumes: - ./consul/data3:/consul/data - ./certs:/consul/certs networks: - vault-consul vault: image: hashicorp/vault:1.15 container_name: vault restart: unless-stopped ports: - "8200:8200" cap_add: - IPC_LOCK environment: VAULT_ADDR: https://0.0.0.0:8200 # Use https VAULT_API_ADDR: https://localhost:8200 # Use https VAULT_LOCAL_CONFIG: | storage "consul" { address = "https://consul:8500" # Use https path = "vault/" tls_ca_file = "/vault/certs/ca.crt" tls_cert_file = "/vault/certs/vault.crt" tls_key_file = "/vault/certs/vault.key" } listener "tcp" { address = "0.0.0.0:8200" tls_cert_file = "/vault/certs/vault.crt" tls_key_file = "/vault/certs/vault.key" client_cert_auth = "require" # Require client certs } ui = true volumes: - ./vault/data:/vault/file - ./certs:/vault/certs # Mount certs depends_on: - consul networks: - vault-consulnetworks: vault-consul: # Define network

Key features of the Docker Compose file:

- A network `vault-consul` is defined and used by both Vault an=d Consul

- Consul ports are mapped individually for each Consul server in the clust=er \(8500, 8502, 8503\)

- Consul TLS settings are included in the command using `-hcl`<=/p>

- Certificates are mounted into both Consul and Vault containers

- Vault addresses are updated to use https

- Consul service definitions are added

# # Kuberne=tes Integration

When moving to Kubernetes, consider the following changes:

1. **Helm Charts** : Use the official Vault and Consul Helm cha=rts

2. **Auto-Unseal** : Configure auto-unseal with cloud provider =KMS

3. **Secret Injection** : Use Vault's Kubernetes auth method fo=r injecting secrets

4. **Service Mesh** : Evaluate Consul Connect for service mesh �pabilities

5. **Storage** : Consider using Consul or integrated storage fo=r Vault

Example Vault Helm values for Kubernetes:

server: ha: enabled: true replicas: 3 extraEnvironmentVars: VAULT_CACERT: /vault/certs/ca.crt VAULT_TLSCERT: /vault/certs/vault.crt VAULT_TLSKEY: /vault/certs/vault.key volumes: - name: certs secret: secretName: vault-certs volumeMounts: - name: certs mountPath: /vault/certs readOnly: true