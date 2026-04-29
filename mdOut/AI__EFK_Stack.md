---
title: "AI+ EFK Stack"
source_file: "AI__EFK_Stack.doc"
converted_date: "2025-09-17T11:24:59.233286"
format: "markdown"
---

# AI+ EFK Stack

The Elasticsearch, FluentBit, and Kibana \(EFK\) stack is a powerf=ul combination of open-source tools designed for centralized log management= and real-time visualization. It allows you to aggregate, process, store, a=nd analyze logs from multiple sources, giving you deep visibility into your= systems.

Much like how _The Simpsons_ set the standard for animated sitcom=s, the EFK stack is the industry gold standard for log processing and analy=tics. Here's why:

\- Scalability: Elasticsearch can handle petabytes of data with distribut� indexing and searching.
\- Real-time log processing: FluentBit processes logs in memory, ensuring lo=w latency.
\- Powerful querying & visualization: Kibana offers rich dashboards, ano=maly detection, and interactive analysis.
\- Efficient resource usage: FluentBit is lightweight, making it ideal for r=esource-constrained environments.
\- Flexible integrations: Works seamlessly with Docker, Kubernetes, and clo=ud platforms.

The purpose of this page is to provide a comprehensive walkthrough for s=etting up the EFK stack for centralized logging. The goal is to collect log=s from the AI+ containers, process them using FluentBit, and visualize them= in Kibana.

NOTE: Obviously, ALL system logs and analytics can be coalesced into thi=s framework. As of this writing, we’re only focused on our utilitie=s.

# **Elasticsearch**

The Elasticsearch components are not available in Ubuntu’s defau=lt package repositories. They can, however, be installed with apt after add=ing Elastic’s package source list.

All of the packages are signed with the Elasticsearch signing key in ord=er to protect the system from package spoofing. Packages that have been aut=henticated using the key will be considered trusted by the package manager.= In this step, we will import the Elasticsearch public GPG key and add the =Elastic package source list in order to install Elasticsearch.

To begin, use cURL, the command line tool for transferring data with URL=s, to import the Elasticsearch public GPG key into APT. Note that we are us=ing the arguments -fsSL to silence all progress and possible errors \(except= for a server failure\) and to allow cURL to make a request on a new locatio=n if redirected. Pipe the output of the `curl` command to the gpg --dearmor command, which converts the key into a format that= `apt` can use to verify downloaded packages.

curl -f=sSL https://artifacts.elastic.co/GPG-KEY-elasticsearch |sudo gpg --dearmor =-o /usr/share/keyrings/elastic.gpg

Copy

Next, add the Elastic source list to the `sources.list.d` dir�tory, where APT will search for new sources:

echo "d� [signed-by=/usr/share/keyrings/elastic.gpg] https://artifacts.elastic.=co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elas=tic-7.x.list

Copy

The `[signed-by=/usr/share/keyrings/elastic.gpg]` portion o=f the file instructs `apt` to use the key that we downloaded to =verify repository and file information for Elasticsearch packages.

Next, update the package lists so apt will read the new Elastic source:<=/p>

sudo ap=t update

Then install Elasticsearch with this command:

sudo ap=t install elasticsearch

Elasticsearch is now installed and ready to be configured.

sudo na=no /etc/elasticsearch/elasticsearch.yml

The `elasticsearch.yml` file provides configuration options f=or your cluster, node, paths, memory, network, discovery, and gateway. Most= of these options are preconfigured in the file but we can change them acco=rding to our needs. For the purposes of our demonstration of a single-serve=r configuration, we will only adjust the settings for the network host.

Elasticsearch listens for traffic from everywhere on port `9200. We will want to restrict outside access to our Elasticsearch instance =to prevent outsiders from reading your data or shutting down your Elasticse=arch cluster through its [REST API] ([https://en.wikipedia.org/wiki/Representat=ional_state_transfer](https://en.wikipedia.org/wiki/Representational=_state_transfer) ). To restrict access and therefore increase secur=ity, find the line that specifies `network.host`, uncomment it, =and replace its value with `localhost` like this:`

/etc/elasticsearch/elasticsear=ch.yml

. . .# ---------------------------------- Network ------------------------------=-----## Set the bind address to a specific IP (IPv4 or IPv6):#network.host: localhost. . .

We have specified `localhost` so that Elasticsearch listens o=n all interfaces and bound IPs. If we want it to listen only on a specific =interface, we can specify its IP in place of `localhost`. Save a=nd close `elasticsearch.yml`.

These are the minimum settings you can start with in order to use Elasti=csearch. Now we can start Elasticsearch for the first time.

Start the Elasticsearch service with `systemctl`. Give Elasti=csearch a few moments to start up. Otherwise, we may get errors about not b=eing able to connect.

sudo sy=stemctl start elasticsearch

Copy

Next, run the following command to enable Elasticsearch to start up ever=y time the server boots:

sudo sy=stemctl enable elasticsearch

Copy

We can test whether your Elasticsearch service is running by sending an =HTTP request:

curl -X= GET "localhost:9200"

Copy

We will see a response showing some basic information about your local n=ode, similar to this:

Output{ "name" : "Elasticsearch", "cluster_name" : "elasticsearch", "cluster_uuid" : "n8Qu5CjWSmyIXBzRXK-j4A", "version" : { "number" : "7.17.2", "build_flavor" : "default", "build_type" : "deb", "build_hash" : "de7261de50d90919ae53b0eff9413fd7e5307301", "build_date" : "2022-03-28T15:12:21.446567561Z", "build_snapshot" : false, "lucene_version" : "8.11.1", "minimum_wire_compatibility_version" : "6.8.0", "minimum_index_compatibility_version" : "6.0.0-beta1" }, "tagline" : "You Know, for Search"}

Elasticsearch allows for Index Lifecycle Management \(ILM\) to automate in�x retention. Initially, we’ll use 60 days as our default. To stor=e logs 60 days and automatically delete old indexes, follow these steps:

curl -X= PUT "localhost:9200/_ilm/policy/aiplus-policy" -H "Content-Type: applicati=on/json" -d '{ "policy": { "phases": { "hot": { "actions": { "rollover": { "max_age": "7d", "max_size": "50GB" } } }, "delete": { "min_age": "60d", "actions": { "delete": {} } } } }}'

This policy:

- **Rolls over the index every 7 days or 50GB** , whichever co=mes first.

- **Deletes indexes older than 60 days**.

Create an index template that uses the ILM policy:

curl -X= PUT "localhost:9200/_index_template/aiplus-template" -H "Content-Type: app=lication/json" -d '{ "index_patterns": ["aiplus-*"], "template": { "settings": { "index.lifecycle.name": "aiplus-policy" } }}'

This ensures that new indexes matching `aiplus-*` follow the =retention policy.

Check that the ILM policy is correctly assigned to an index:

curl -X= GET "localhost:9200/aiplus-000001/_ilm/explain?pretty"

If correctly configured, we should see the ILM policy name in the output=.

To delete an old index manually:

curl -X= DELETE "localhost:9200/aiplus-2024.01.01"

To check disk usage for indexes, use the following command:

curl -X= GET "localhost:9200/_cat/indices?v&h=index,store.size"

#
**FluentBit**

Fluent Bit is available as the `fluent-bit` package and suppo=rts long-term releases of Ubuntu.

To install the most recent version, we can use the following script:

curl ht=tps://raw.githubusercontent.com/fluent/fluent-bit/master/install.sh | sh

This script is a convenience helper and should be reviewed before use. F=or a secure deployment, follow the steps below.

## # **Secure Installation =Steps**

To ensure we receive the correct signed packages, we add the Fluent Bit =server GPG key:

curl ht=tps://packages.fluentbit.io/fluentbit.key | gpg --dearmor > /usr/share/k=eyrings/fluentbit-keyring.gpg

The updated GPG key \(March 2022\) has the fingerprint:

C3C0 A2� 34B9 293E AF51 FABD 9F9D DC08 3888 C1CD

We add the following entry to `/etc/apt/sources.list`, replac=ing `${CODENAME}` with our Ubuntu release name \(e.g., `foca=l` for 20.04\):

deb [si=gned-by=/usr/share/keyrings/fluentbit-keyring.gpg] https://packages.fluen=tbit.io/ubuntu/${CODENAME} ${CODENAME} main

We refresh the package database:

sudo ap=t-get update

To prevent issues with expired certificates, we upgrade the system:

sudo ap=t-get upgrade

If we encounter certificate verification errors, we should first ensure =the `ca-certificates` package is installed:

sudo ap=t-get install ca-certificates

We install Fluent Bit using:

sudo ap=t-get install fluent-bit

Edit `/etc/fluent-bit/fluent-bit.conf`:

[SERVIC=E] Flush 1 Log_Level info Parsers_File parsers.conf[INPUT] Name forward Listen 0.0.0.0 Port 24224# Apply AIPlus custom parser to JSON logs[FILTER] Name parser Match docker.* Parser aiplus-docker-json Key_Name log Reserve_Data true[OUTPUT] Name es Match docker.* Host localhost Port 9200 Index aiplus Logstash_Format On Logstash_prefix aiplus Retry_Limit 5

[PARSER=] Name aiplus-docker-json Format json Time_Key timestamp Time_Format %Y-%m-%d %H:%M:%S[PARSER] Name aiplus-docker-plain Format regex Regex ^(?<log>.*)$

Then, we start the service:

sudo sy=stemctl start fluent-bit

To confirm it is running, we check the service status:

systemc=tl status fluent-bit

Expected output:

�=8F fluent-bit.service - Fluent Bit Loaded: loaded (/lib/systemd/system/fluent-bit.service; disabled; vendor= preset: enabled) Active: active (running) since [timestamp] Main PID: [process_id] (fluent-bit) Tasks: 1 Memory: [memory_usage] CPU: [cpu_time] CGroup: /system.slice/fluent-bit.service └─[process_id] /opt/fluent-bit/bin/fluent-bit -c= /etc/fluent-bit/fluent-bit.conf

By default, Fluent Bit collects CPU usage metrics and logs them to /var/log/syslog.

# **Kibana**

According to the [official documentation](https://www.elastic.=co/guide/en/elastic-stack/current/installing-elastic-stack.html), we should install Kibana only after inst=alling Elasticsearch. Installing in this order ensures that the components �ch product depends on are correctly in place.

Because we’ve already added the Elastic package source in the pr=evious step, we can just install the remaining components of the Elastic St�k using `apt`:

sudo ap=t install kibana

Copy

Then enable and start the Kibana service:

sudo sy=stemctl enable kibana

Copy

Edit `/etc/kibana/kibana.yml`:

server.=port: 5601server.host: "0.0.0.0"server.publicBaseUrl: "https://10.161.0.92:5601"elasticsearch.hosts: ["http://localhost:9200"]server.ssl.enabled: trueserver.ssl.certificate: /etc/kibana/kibana-server.crtserver.ssl.key: /etc/kibana/kibana-server.key

sudo sy=stemctl enable --now kibana

Verify Kibana is running:

sudo sy=stemctl status kibana

Open Kibana in a browser:

https:/=/10.161.0.92:5601

To access Kibana directly via HTTPS \(`https://<remote-IP-address=>:5601`\), follow these steps:

openssl= genrsa -out kibana-server.key 2048openssl req -new -key kibana-server.key -out kibana-server.csropenssl x509 -req -days 1095 -in kibana-server.csr -signkey kibana-server.k=ey -out kibana-server.crt

The STRONGLY PREFERRED alternative to self-signed certificates is a corp=orate CA. We should request certificates from our customer’s intern=al certificate authority if available.

Edit `/etc/kibana/kibana.yml`:

server.=ssl.enabled: trueserver.ssl.certificate: "/etc/kibana/kibana-server.crt"server.ssl.key: "/etc/kibana/kibana-server.key"

Ensure the proper file permissions\!

sudo mv= kibana-server.key kibana-server.crt /etc/kibana/sudo chown kibana:kibana /etc/kibana/kibana-server.keysudo chmod 400 /etc/kibana/kibana-server.keysudo chmod 444 /etc/kibana/kibana-server.crt

sudo sy=stemctl restart kibana

sudo sy=stemctl status kibana

### # ****

# **Debugging and Validat=ion**

Check FluentBit Logs

sudo jo=urnalctl -u fluent-bit -n 50 --no-pager

Verify Elasticsearch Indexes

curl -X= GET "http://localhost:9200/_cat/indices?v"

Query Elasticsearch for Logs

curl -X= GET "http://localhost:9200/aiplus-*/_search?pretty=true" -H 'Content-Typ=e: application/json' -d '{"size": 10, "query": {"match_all": {}}}'