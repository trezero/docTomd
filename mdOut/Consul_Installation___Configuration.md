---
title: "Consul Installation & Configuration"
source_file: "Consul_Installation___Configuration.doc"
converted_date: "2025-09-17T11:24:59.336658"
format: "markdown"
---

# Consul Installation & Configuration

# # Prerequisites

- Consul installed via vanilla installation.

- Access to servers running Consul.

- Let’s Encrypt certificates configured for your domain \(e.g., lambda1.aiplus.perifery.com\).

- * *

# # <=strong>Step 1: Vanilla Installation

## # 1\. <=strong>Consul Setup Directory

Create a universal path for Consul files:

CONSUL_�SE="${HOME}/consul" mkdir -p "${CONSUL_BASE}/setup" "${CONSUL_BASE}/data/{checks,services}" "${=CONSUL_BASE}/certs"

## # 2\. Download Binaries

cd "${C=ONSUL_BASE}/setup"wget https://releases.hashicorp.com/consul/1.21.1/consul_1.21.1_linux_amd64=.zipunzip consul_1.21.1_linux_amd64.zip

### # 3\. Move Consul to `~/bin`****

mkdir -=p ~/bin mv consul ~/bin/

### # 4\. Add `~/bin`**to Your**`PATH`

echo 'e=xport PATH="$HOME/bin:$PATH"' >> ~/.bashrcsource ~/.bashrc

### # 5\. Verify Installation

consul =--version

_\(Should output:_`Consul v1.21.1` _\)_

- * *

# # Step 2: TLS Configuration

## # 1\. Symlinking Let's Encrypt Certificates for Consul

ln -sf =/etc/letsencrypt/live/yourdomain.com/fullchain.pem "${CONSUL_BASE}/certs/"ln -sf /etc/letsencrypt/live/yourdomain.com/privkey.pem "${CONSUL_BASE}/cer=ts/"ln -sf /etc/letsencrypt/live/yourdomain.com/chain.pem "${CONSUL_BASE}/certs=/"

## # 2\. Create Config File \(`${CONSUL_BASE}/consu=l-secure.hcl`\)

datacen=ter = "dc1"data_dir = "${CONSUL_BASE}/data"server = truebootstrap_expect = 1node_name = "lambda1-dev"# Networkbind_addr = "YOUR_SERVER_IP" advertise_addr = "YOUR_SERVER_IP"client_addr = "0.0.0.0" # TLStls { defaults { cert_file = "${CONSUL_BASE}/certs/fullchain.pem" key_file = "${CONSUL_BASE}/certs/privkey.pem" ca_file = "${CONSUL_BASE}/certs/chain.pem" verify_incoming = true verify_outgoing = true } https { verify_incoming = false } grpc { use_auto_cert = false }}# UIui_config { enabled = true}# Portsports { https = 8500 http = -1 grpc = -1 grpc_tls = 8503}

- * *

# # **S=tep 3: Start Consul**

~/bin/c=onsul agent -dev -config-file="${CONSUL_BASE}/consul-secure.hcl"

Once the agent is running, you can access the Consul Web UI securely via= HTTPS:

**UI URL:** [https://10.161.244.15:8500/ui](https://10.1a.244.15:8500/ui) \(for =the `lambda1` server\)