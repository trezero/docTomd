---
title: "Security Validation"
source_file: "Security_Validation.doc"
converted_date: "2025-09-17T11:24:59.462570"
format: "markdown"
---

# Security Validation

# # 1\. All Comm=unications Use TLS

- All plain HTTP requests are correctly rejected.

- TLS handshakes complete successfully.

- No plaintext ports are exposed.

## # 1.1. HTTP Port P=roperly Rejected

curl ht=tp://lambda1.aiplus.perifery.com:8500/

**Result** : `400 Bad Request - Client sent HTTP to HTT=PS server`

- Plain HTTP is not accepted, as expected.

- * *

## # 1.2. HTTPS Port Respond=s

curl ht=tps://lambda1.aiplus.perifery.com:8500/

**Result** : TLS handshake completes successfully \(a certifi�te warning may appear due to hostname mismatch\)

- Communication is encrypted with TLS.

- * *

## # 1.3. No Pla=intext Ports Open for Consul

netstat= -tulnp | grep consul

**Result** : Only TLS-capable ports like `8301`, =`8302`, and `8500` are open.

- No unencrypted \(plaintext\) ports are listening.

- * *

## # 1.4. UI Access Verif=ication

- Open browser: `https://10.161.244.15:8500/ui`

- Click "Advanced" → "Proceed to site" \(to bypass certificate warn=ing\)

- Expected result: Consul UI loads successfully

**Status** : UI is accessible only over HTTPS.

- Certificate warning exists due to hostname mismatch, but it **does= not affect encryption or security**

- * *

# # =2. Service Discovery Works Over Secure Connections

- Services can **find each other** through Consul

- All discovery communications are **encrypted** \(no plaintex=t\)

- Services get correct connection info \(hostnames, ports\)

- Everything works **without any HTTP/unencrypted fallback** <=/p>

## # 2.1. Enforce HTTPS-Only Registration \(Using Domain Name + CA C=ert\)

## # 2.1.1. HT=TPS Registration \(Should Pass\)

curl --�cert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem -X PUT -=d '{ "ID": "test-https", "Name": "test-https", "Address": "lambda1.aiplus.perifery.com", "Port": 8080}' "https://lambda1.aiplus.perifery.com:8500/v1/agent/service/register"

- Uses HTTPS and valid cert.

- Service registered securely.

- * *

## # 2.1.2. HTTP= on HTTPS Port \(Should Fail\)

curl -k= -X PUT -d '{ "ID": "test-http", "Name": "test-http", "Address": "lambda1.aiplus.perifery.com", "Port": 8080}' "http://10.161.244.15:8500/v1/agent/service/register"

Expected Output:

curl: (=1) Received HTTP/0.9 when not allowedClient sent an HTTP request to an HTTPS server.

- `http://` used on a TLS-only port.

- Protocol mismatch error — registration blocked.

- * *

## # 2.2. Testi=ng using two FastAPI services

These are two FastAPI services running on ports `11003` and <=code>11004, built for testing service discovery. This approach can a=lso be extended to any HTTPS service such as Metagen, Facial Recognition, e=tc.

## # 2.2.1 Valida=te Service Registration

# List =all services (HTTPS only)consul catalog services \ -http-addr="https://lambda1.aiplus.perifery.com:8500" \ -ca-file=/etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem# Check service detailscurl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ "https://lambda1.aiplus.perifery.com:8500/v1/catalog/service/service-a"

- * *

## # 2.2.2 Tes=t Service Discovery Mechanisms

### # DNS-Based Discovery

dig @12=7.0.0.1 -p 8600 service-a.service.consul +shortdig @127.0.0.1 -p 8600 service-b.service.consul +short

### # API-Based Discovery

# From =Service-A (discover Service-B)curl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem = "https://lambda1.aiplus.perifery.com:11004/discover-services?service_name=3Dservice-b"# From Service-B (discover Service-A)curl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ "https://lambda1.aiplus.perifery.com:11003/discover-services?service_name=3Dservice-a"# From Service-B (discover Consul)curl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ "https://lambda1.aiplus.perifery.com:11003/discover-services?service_name=3Dconsul"

- * *

## # 2.=2.3 Verify Service-to-Service Communication

### # HTTPS Communic=ation \(Should Pass\)

# Servi�-A → Service-Bcurl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ https://lambda1.aiplus.perifery.com:11003/health# Service-B → Service-Acurl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ https://lambda1.aiplus.perifery.com:11004/health

### # HTTP Communicat=ion \(Should Fail\)

# Servi�-A → Service-B (HTTP)curl http://lambda1.aiplus.perifery.com:11003/health# Service-B → Service-A (HTTP)curl http://lambda1.aiplus.perifery.com:11004/health

Expected Output:

curl: (R) Empty reply from server

- * *

## # 2.3. Certificate Va=lidation

# Verif=y Consul's certificateopenssl s_client -connect lambda1.aiplus.perifery.com:8500 \ -CAfile /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem# Verify Service-A's certificateopenssl s_client -connect lambda1.aiplus.perifery.com:11004 \ -CAfile /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem

- * *

# # **3.= Consul UI is Accessible Only via HTTPS**

- The Consul web interface **cannot** be accessed using http://

- All access must use `https://`

- Any attempt to use HTTP should automatically redirect to HTTPS or be blo=cked

## # 3.1. HTTP Access is B=locked

curl ht=tp://lambda1.aiplus.perifery.com:8500/ui

**Expected Output:**

HTTP/1.=0 400 Bad RequestClient sent an HTTP request to an HTTPS server.

- **Correct** : Confirms that port `8500` is config=ured to expect HTTPS only and rejects HTTP.

- * *

## # 3.2. HTTPS Access Works<=/h3>

curl ht=tps://lambda1.aiplus.perifery.com:8500/ui

**Expected Output:**

< HT=TP/2 301< location: /ui/

- A **successful TLS handshake** occurs.

- A **301 redirect** from `/ui` to `/ui/ is expected from Consul UI.`

- Certificate is valid \(issued by **Let’s Encrypt** f=or `lambda1.aiplus.perifery.com`\).

- * *

## # 3.3. Port Co=nfiguration Looks Secure

netstat= -tulnp | grep consul

**Expected Output:**

tcp6 ::=:8500 :::* LISTEN

- Only **HTTPS port \(8500\)** is open.

- No unencrypted port exposed.

- * *

## # 3.4. Browser Test

- Navigating to `http://10.161.244.15:8500/ui` fails or trigger=s a redirect.

- Navigating to `https://10.161.244.15:8500/ui/` loads the Cons=ul UI.

- * *

# # 4.**Configuration changes propagate correctly over s�ure connections**

## # **4.1. KV Stor=e Security Tests**

## # Write/Read Encrypted �ta

# Write= secure valuecurl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ -X PUT -d 'secure-value' \ "https://lambda1.aiplus.perifery.com:8500/v1/kv/secure-test"# Read back valuecurl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ "https://lambda1.aiplus.perifery.com:8500/v1/kv/secure-test?raw"

**Expected Results** :

- PUT → Returns `true`

- GET → Returns `secure-value`

- * *

## # **4.2. =Service Registration Security**

## # Register/Verify H=TTPS Service

# Regis=ter new servicecurl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ -X PUT -d '{ "ID": "test-https", "Name": "test-https", "Address": "lambda1.aiplus.perifery.com", "Port": 8443, "Tags": ["https-only"] }' "https://lambda1.aiplus.perifery.com:8500/v1/agent/service/register"# Verify registrationcurl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ "https://lambda1.aiplus.perifery.com:8500/v1/catalog/service/test-https" =| jq

**Expected Results** :

- Returns JSON with service details including `"https-only"` ta=g

- * *

## # **4.3. Negative Tests=**

## # Attempt Unencryp=ted Operations

# Try H=TTP service registrationcurl -X PUT -d '{ "ID": "test-http", "Name": "test-http", "Port": 8080}' "http://lambda1.aiplus.perifery.com:8500/v1/agent/service/register"# Try HTTP KV writecurl -X PUT -d 'insecure' "http://lambda1.aiplus.perifery.com:8500/v1/kv/in=secure-test"

**Expected Results** :

Both commands return:

`Client sent an HTTP request to an HTTPS server`

- * *

## # **4.4. Network= Configuration**

## # Verify Listening Ports

ss -tul=np | grep -E '8300|8302'

**Expected Results** :

tcp LI=STEN 0 4096 10.161.244.15:8300 0.0.0.0:* users:(("consul",pid=XXX,fd=X=X))tcp LISTEN 0 4096 10.161.244.15:8302 0.0.0.0:* users:(("consul",pid=XXX=,fd=XX))

- * *

## # **4.5. Con=figuration Persistence**

## # Test Reload and Pers=istence

# Trigg=er reloadcurl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ -X PUT "https://lambda1.aiplus.perifery.com:8500/v1/agent/reload"# Verify services persistcurl --cacert /etc/letsencrypt/live/lambda1.aiplus.perifery.com/chain.pem \ "https://lambda1.aiplus.perifery.com:8500/v1/catalog/services" | jq

**Expected Results** : All previously registered services re=main listed.

- * *

For more reference:

- [AI-356: AI+ System TLS/mTLS Implementation Guide](https://perifery.atlassian.net/wiki/wiki/spaces/AI/pages/4220\(9050/AI-356+AI+System+TLS+mTLS+Implementation+Guide)

- [AI-354 - AI+ Configuration and Security](https://perifery.atlassian.net/wiki/wiki/spaces/AI/pages/4199�2929/AI-354+-+AI+Configuration+and+Security)