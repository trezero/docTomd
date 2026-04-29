---
title: "AI-356: AI+ System TLS/mTLS Implementation Guide"
source_file: "AI-356__AI__System_TLS_mTLS_Implementation_Guide.doc"
converted_date: "2025-09-17T11:24:58.999716"
format: "markdown"
---

# AI-356: AI+ System TLS/mTLS Implementation Guide

This guide documents our approach to implementing Transport Layer Securi=ty \(TLS\) and mutual TLS \(mTLS\) across the AI+ system. We'll be securing com=munications between all components in our architecture, including the Notif=icationAPI gateway, microservices \(Metagen, VisageAI, ObjectRecognition, et=c.\), vector databases \(Chroma, Milvus\), and Hashicorp tools \(Consul, Vault\)=. Per corporate requirements, we're using Let's Encrypt certificates for al=l TLS implementations.

# # Architecture Strategy

Our TLS implementation follows a phased approach:

Phase 1: Let's Encrypt with Shared Certificates

- Single certificate with Subject Alternative Names \(SANs\) for all service=s

- Filesystem-based certificate storage

- Automated renewal via certbot

- Simple certificate distribution through file system

Phase 2: Vault-based PKI Implementation

- Vault as certificate authority

- Dynamic certificate generation

- Service-specific certificates with shorter lifetimes

- Automated rotation handled by Vault

# # Doma=in Structure

For our internal systems, we're using a subdomain structure under [a=iplus.perifery.com](http://aiplus.perifery.com):

- Each internal system gets its own CN: \[system-name\].aiplus.perifery.com<=/p>

- All services within a system are included as SANs

- DNS managed through Route53

Example for our lambda2 system:

- CN: [lambda2.aiplus.perifery.com](http://lambda2.aiplus.perifery.co=m)

- SANs:

- [notificationapi.lambda2.aiplus.perifery.com=](http://notificationapi.lambda2.aiplus=.perifery.com)

- [metagen.lambda2.aiplus.perifery.com](http://metagen.lambda2.aiplus.perifer=y.com)

- [visageai.lambda2.aiplus.perifery.com](http://visageai.lambda2.aiplus.perife=ry.com)

- etc.

For customer systems, the domain structure is yet to be finalized. Howev=er, we're strongly considering using our own domain structure in the form o=f \[customer-name\].aiplus.perifery.com. This approach offers several advanta=ges. First, it gives us complete control over DNS management and certificat=e issuance/renewal, eliminating dependencies on customer DNS teams that cou=ld delay updates. Second, using our domain simplifies our certificate manag=ement infrastructure, allowing consistent processes across all deployments.= Finally, this standardization makes scaling our operations more straightfo=rward, as we don't need to develop customer-specific certificate handling p=rocesses.

Since we own the Perifery domain and have full control through Route53, =we can easily automate Let's Encrypt certificate issuance and renewal using= the certbot DNS plugin for Route53. This provides a fully automated certif=icate management solution without needing HTTP validation, which is particu=larly useful for services that aren't publicly accessible.

While using customer domains might seem more "native" to their environme=nts, the operational complexity it introduces often outweighs the benefits.= Our experience shows that certificate management is a significant operatio=nal burden that's best kept under our control. Additionally, since our serv=ices are typically accessed through customer applications rather than direc=tly by end users, the domain names are largely transparent to users.

# # Air-Gapped Environments

For deployment in air-gapped environments \(such as government agencies\),= special consideration will be needed during Phase 2 of our implementation.= When configuring Vault as a certificate authority, these environments pres=ent unique challenges as they have no internet connectivity, making Let's E=ncrypt certificate issuance impossible through standard methods.

For Phase 2 in air-gapped environments, we will need to adapt our Vault =PKI implementation:

1. **Customer-provided root/intermediate CA** : Instead of usin=g Let's Encrypt certificates as our intermediate CA in Vault, we would impo=rt the customer's existing internal CA certificates. Vault would then issue= service certificates chained to their trusted root.

2. **Offline CA initialization** : We would initialize Vault's =PKI engine using an offline process, generating and signing the intermediat=e CA before deployment, then importing it into the air-gapped Vault instanc=e.

3. **HSM integration with Vault** : For high-security environme=nts, Vault can be configured to use Hardware Security Modules for cryptogra=phic operations, keeping private keys in tamper-resistant hardware.

This specialized approach is not in scope for Phase 1 of our implementat=ion, which focuses on standard environments with internet connectivity. The= air-gapped implementation details will be developed specifically for Phase= 2 as needed for particular customer requirements.

# # Certificate Acquisition and Management

For our Phase 1 implementation, we obtain a single Let's Encrypt certifi�te containing all service domains as Subject Alternative Names:

sudo ce=rtbot certonly --standalone \ --email admin@perifery.com \ --agree-tos \ -d lambda2.aiplus.perifery.com \ -d notificationapi.lambda2.aiplus.perifery.com \ -d metagen.lambda2.aiplus.perifery.com \ # ... additional service domains

This approach simplifies certificate management while still providing pr=oper TLS security for each service.

We automate certificate renewal using a simple cron job that:

1. Attempts to renew certificates via certbot

2. Copies renewed certificates to a shared location

3. Distributes certificates to all servers

4. Signals services to reload certificates when necessary

The renewal script runs monthly but only actually renews certificates wh=en they're within 30 days of expiration.

# # AI+ Common=

Our Common Library implementation abstracts certificate management and p=rovides a consistent interface for enabling TLS/mTLS in all services.

We will create an abstract provider interface that decouples certificate= acquisition from usage. This separation allows us to swap implementation d=etails without changing service code. In Phase 1, we use a simple provider =that reads certificates from the filesystem.

# Basic c=ertificate provider interfaceclass CertificateProvider: def get_certificate(self): """Return tuple of (cert_path, key_path, ca_path)""" pass

In Phase 2, we'll use a provider that obtains certificates dynamically f=rom Vault. This abstraction is key to our phased approach, allowing service=s to transition gradually without code changes.

class Vau=ltCertificateProvider(CertificateProvider): def get_certificate(self): # We will authenticate to Vault and request certificate, etc... return (cert_path, key_path, ca_path)

The TLS configuration handles certificate validation, SSL context creati=on with secure defaults, TLS version management \(supporting TLS 1.2/1.3\), c=ipher suite selection, and mTLS options for client certificate validation. =We've implemented sane defaults that work out-of-the-box but can be customi=zed when needed. The default TLS configurations are:

- Minimum TLS version: 1.2

- Preferred cipher suites: \[List the suites\] \(Add the list of cipher suite=s here\)

- Certificate validation: Enabled, using the system's trust store.

def run=_with_https(app, host="0.0.0.0", port=8443): cert_provider = FileCertificateProvider() # Or VaultCertificateProvi�r cert_path, key_path, ca_path = cert_provider.get_certificate() uvicorn.run( app, host=host, port=port, ssl_certfile=cert_path, ssl_keyfile=key_path )

The library provides simple integration with FastAPI applications throug=h middleware for security headers \(HSTS\), Uvicorn configuration for HTTPS, =and graceful fallback if certificates aren't available. The library handles= certificate loading/validation failures as follows:

- If certificates are unavailable at startup: The service will log an erro=r and may terminate, depending on a configuration setting. The default beha=vior is to terminate.

- If a certificate becomes invalid during runtime: The service will log an= error and attempt to reload. If reloading fails, the service will terminat=e.

Our implementation specifically addresses mutual TLS requirements:

- Server Certificate Validation: All services validate certificates presen=ted by servers they connect to

- Client Certificate Validation: Services can optionally require and valid=ate client certificates. This is configured using the require\_client\_cert f=lag in the TLS configuration. When set to True, the server will request and= validate client certificates.

- Certificate Issuance Control: We control who can obtain valid certificat=es

This creates a zero-trust security model where both the client and serve=r validate each other's identity.

# # Do=cker Integration

In containerized environments, certificates need to be accessible inside= the containers while maintaining security. Here's our approach for each ph=ase:

Phase 1: Filesystem-based Certificates

In Phase 1, we map the host certificate directory into containers as a r�d-only volume:

# Conce=ptual Docker Compose exampleservices: microservice: volumes: - /etc/aiplus/certs/shared:/app/certs:ro environment: - SSL_CERT_FILE=/app/certs/fullchain.pem - SSL_KEY_FILE=/app/certs/privkey.pem

The /etc/aiplus/certs/shared directory on the host contains the shared c=ertificates. This directory is mapped to /app/certs inside each container. =The :ro flag ensures certificates are read-only within containers. Environm=ent variables tell the application where to find the certificates. Certific=ate renewal only requires updating files on the host. The distribution of t=hese updated certificates to the hosts is handled by secure copy, or even T=erraform. Access to the certificate directory on the host is restricted to =the root user and the cert-manager group, with read-only permissions for th=e group.

In Phase 2, containers will obtain certificates directly from Vault:

# Conce=ptual Docker Compose example for Phase 2services: microservice: environment: - VAULT_ADDR=https://vault.lambda2.aiplus.perifery.com:8200 - VAULT_ROLE=microservice # Service will use these to authenticate to Vault - VAULT_TOKEN_PATH=/run/secrets/vault-token secrets: - vault-token

In this approach, no certificate volumes are needed. Services authentica=te to Vault and request certificates on startup. Certificates are stored in= memory or in ephemeral storage. Certificate renewal happens automatically =through Vault. Each service receives a unique certificate appropriate for i=ts identity.

The VAULT\_TOKEN\_PATH environment variable points to a file containing a =Vault token. This token is provisioned as a Kubernetes secret \(or Docker se=cret, if not in Kubernetes\) and mounted into the container. The token has a= limited lifetime and is rotated automatically using Vault Agent with auto-=auth, leveraging a more secure authentication method such as AppRole.

Local Installation

I'll create a detailed wiki section on managing certificates for local T=LS/mTLS development.

# Local TLS/mTLS Development

This section is strictly for configuring locally-run microservices to ac�ss Let's Encrypt certificates on a development environment. These steps e=nsure TLS/mTLS functions properly during local development while using the =same production certificates.

Note that this section applies ONLY to **development**. We =should not be changing groups or ownership in production\!

# # Certificate Access Configuration

The easiest way to get access to the certs is to change the group owners=hip. On the Lambda machines, there is a group called “aiplus�=9D we use for managing access to shared resources.

# Creat=e a dedicated group for certificate access (if it doesn't exist)sudo groupadd aiplus

We will need to configure Directory and File Permissions

# Set p=roper group permissions on certificate directoriessudo chmod 755 /etc/letsencryptsudo chmod 755 /etc/letsencrypt/livesudo chmod 750 /etc/letsencrypt/archive# Set group ownershipsudo chgrp aiplus /etc/letsencrypt/livesudo chgrp -R aiplus /etc/letsencrypt/archive/lambda2.aiplus.perifery.com# Make certificate files readable by the groupsudo chmod -R g+rx /etc/letsencrypt/archive/lambda2.aiplus.perifery.com# Ensure private keys have restricted permissionssudo chmod 640 /etc/letsencrypt/archive/lambda2.aiplus.perifery.com/privkey=1.pem# Set execute bit on necessary directories to make symlinks traversablesudo chmod g+x /etc/letsencrypt/archivesudo chmod g+x /etc/letsencrypt/archive/lambda2.aiplus.perifery.com

Make sure the username is added to the group that owns the certificate.<=/p>

# Add y=our user to the certificate access groupsudo usermod -a -G aiplus <username>

In Consul, we will need to update each service's configuration to use th=e Let's Encrypt certificates:

tls: enabled: true provider_type: file certificate: file: cert_dir: /etc/letsencrypt/live/lambda2.aiplus.perifery.com cert_file: fullchain.pem key_file: privkey.pem

# # Hostname Configuration

If the CN and SANs do not map to an IP address, accessing the FastAPI pa=ge on the machine will produce security warnings. To address these certific=ate name validation issues, the easiest thing to do is map the IP address t=o the host.

# Add e=ntries to /etc/hostssudo nano /etc/hosts# Add lines like:127.0.0.1 lambda2.aiplus.perifery.com127.0.0.1 asr-service.lambda2.aiplus.perifery.com127.0.0.1 vlm-service.lambda2.aiplus.perifery.com# Add all relevant service hostnames

We can also update the service configuration to use the hostnames that m=atch the certificate:

# Examp=le configurationconfig.update({ "service": { "host": "asr-service.lambda2.aiplus.perifery.com", "port": 8443 }})

# # Troubleshooting Certificate Access

Here’s some simple and easy steps we can take if we encounter de=bugging issues.

1. **Verify group membership** :

groups =<username>

Ensure `aiplus` appears in the list. You may need to log out =and back in for group changes to take effect.

2. **Check file ownership and permissions** :

ls -la =/etc/letsencrypt/live/lambda2.aiplus.perifery.com/ls -la /etc/letsencrypt/archive/lambda2.aiplus.perifery.com/

Verify group ownership and permissions are correct.

3. **Test certificate accessibility** :

openssl= x509 -in /etc/letsencrypt/live/lambda2.aiplus.perifery.com/fullchain.pem -=text -noout

This command should run without permission errors.

# # Certificate Renewal Considerations

When Let's Encrypt certificates are renewed:

1. The symlinks in `/etc/letsencrypt/live/` will point to new fi=les

2. We need to ensure the renewal process maintains the correct permissions<=/p>

3. We should add a post-renewal hook to fix permissions:

# Add t=o /etc/letsencrypt/renewal-hooks/post/fix-permissions.sh#!/bin/bashchgrp -R aiplus /etc/letsencrypt/archive/lambda2.aiplus.perifery.comchmod -R g+rx /etc/letsencrypt/archive/lambda2.aiplus.perifery.comchmod 640 /etc/letsencrypt/archive/lambda2.aiplus.perifery.com/privkey*.pem

# # Consul and Vault TLS Configuration

Consul requires certificates for both its server-to-server and client-to=-server communications. Our approach is to mount certificates into Consul c=ontainers, configure TLS settings to require verification for both incoming= and outgoing connections, disable HTTP endpoints \(forcing all API communic=ations over HTTPS\), and enable Consul Connect with TLS for service mesh cap�ilities.

Verify both incoming and outgoing connections, use the shared certificat=e for server identification, secure RPC, HTTP and gossip protocols, and set= minimum TLS version to 1.2.

Consul Connect will use the certificates to establish mTLS connections b=etween services. Each service will present its certificate to other service=s, and verify the certificates of the services it connects to, based on the= service identity provided by Consul.

Vault's TLS configuration is similar but includes additional settings fo=r its role as a certificate authority. We secure the Vault API and UI with =TLS, configure the PKI secrets engine for certificate issuance \(Phase 2\), s=et up certificate roles that map to service types, and implement authentica=tion methods for services to obtain certificates.

# # Vault PKI Implementation

In Phase 2, we'll leverage Vault's PKI secrets engine to enhance our cer=tificate management.

For initial setup, we configure Vault's PKI secrets engine, set up a cer=tificate authority hierarchy, and define certificate roles and policies.

To use our Let's Encrypt certificate as an intermediate CA in Vault:

# 1. Im=port the Let's Encrypt certificate chain and private key into Vaultvault write pki/config/ca \ pem_bundle=@/etc/aiplus/certs/shared/fullchain-and-key.pem# 2. Set up a role for issuing service certificatesvault write pki/roles/service-role \ allowed_domains="lambda2.aiplus.perifery.com,*.lambda2.aiplus.perifery.=com" \ allow_subdomains=true \ max_ttl="72h"

The imported Let's Encrypt certificate serves as an intermediate CA that= Vault uses to sign service certificates. This maintains the trust chain ba=ck to Let's Encrypt while allowing Vault to dynamically issue certificates.= Since Let's Encrypt certificates expire after 90 days, we'll need to updat=e the Vault CA configuration when we renew our Let's Encrypt certificates.<=/p>

For service integration, services authenticate to Vault using appropriat=e credentials, request certificates with specific parameters \(CN, SANs, TTL=\), Vault issues short-lived certificates \(24-72 hours\), and services automa=tically renew certificates before expiration.

The advantages of this approach include dynamic certificate issuance, au=tomatic rotation, fine-grained access control, comprehensive audit logging,= and shorter certificate lifetimes for enhanced security.

# # =Kubernetes Migration

When transitioning to Kubernetes, our TLS implementation will evolve:

- Certificate Storage: Using Kubernetes Secrets instead of filesystem

<=/li>
- Certificate Distribution: Leveraging Kubernetes mechanisms

- Vault Integration: Using Kubernetes auth methods for Vault integration

This will be detailed further when we begin Kubernetes migration plannin=g.