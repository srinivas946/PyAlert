# PyAlert
PyAlert is an Security Incident and Event Management Tool. It is designed completely with Python, It’s a basic tool architecture to understand how SIEM Works in real time. This tool interact with ELK Stack to fetch datasources Information such as Logs. You can Integrate as many datasources you want by simple configuration and write own parsers for different log formats. PyAlert Provides Command line interface for user Interaction.
<br/>
### Features List
PyAlert come up with list of features
- Alerting
- Reporting
- Health Check
### Architecture
![PyAlert Architecture](Images/architechture.jpg)
### Architecture Components
#### Elastic Search
- Elasticsearch is a distributed search and analytics engine
- It Provides real time search and analytics for all types od data (sturctured or unstructured text, numericals etc..)
- Elasticsearch offers speed and flexibility to handle data in wide variety of use cases
- Elasticsearch store data in the form of index to perform fast searches.
- It build on the top of Apache Lucene Library
- Elasticsearch provides REST API to communicate with it for fetching the Stored Information
- To Know more about Elasticsearch, Refer : https://www.elastic.co/guide/en/elasticsearch/reference/7.6/index.html

#### Logstash
- Horizontal scalable data processing pipeline with strong Elasticsearch and Kibana Synergy
- Logstash collects the data from different data sources and normalizes the data into destinations of your choice
- Any type of event can be enriched and transformed with broad array of input filters and output plugins
- Over 200 plugins are avaiable in logstash version 7.5
- Logstash provides Input Plugins to get logs from Datasources, Filters to normalize the data, Output Plugins to send data to destinations such as ElasticSearch or Kibana etc..
- To Know more about Logstash, Refer : https://www.elastic.co/guide/en/logstash/7.6/index.html

#### Data Sources
- <b>Beats</b>
  - Beats are light weight shippers for forwarding and centralizing logs data
  - It can installed as an agent on your servers
  - Beats monitor the log files or locations that you specify, collect log events and forward them to Logstash
  - In Beats Family we have multiple type of beats
    - <b>File beat</b> are Light weight shippers for logs data
    - <b>Metric beat</b> are Ligh weight shippers for Metrics (CPU Usaeg, Memory, File System, disk IO etc.)
    - <b>Packet beat</b> enables you to access this data to understand how traffic is flowing through your network
    - <b>Winlog beat</b> enales you to access windows related logs such as security Logs, Appplication Logs etc.
  - To Learn More about beats, Refer : https://www.elastic.co/beats/
- <b>Syslog</b>
  - Syslog stands for System Logging.
  - It is a standard protocol used to send system log or event messages to a specific server called Syslog Server.
  - In Logstash, syslog is one of the input plugin to collect the logs
  - Generally, syslog works on the port 514
  - To Know more about Syslog input plugin for Logstash, Refer : https://www.elastic.co/guide/en/logstash/current/plugins-inputs-syslog.html
- <b>Database</b>
  - You can also pull the database logs using jdbc plugin provided by logstash
  - You can integrate database irrespective of it type (eg: mysql, mongodb etc.)
  - To know more about Jdbc Input plugin for Logstash. Refer : https://www.elastic.co/guide/en/logstash/current/plugins-inputs-jdbc.html
- <b>Other Available Plugins</b>
  - Logstash comes with lot of input plugins by default
  - Input Plugins available - Kafka, Salesforce, log4j, http, twitter, azure event hubs, Cloud watch, xmpp, wmi etc.
  - To know the list of all available plugins, Refer : https://www.elastic.co/guide/en/logstash/current/input-plugins.html
  - If you want to install new plugin, logstash provide command line interface to do so

#### PyAlert
  - Security Incident and Event Manangement Tool completely designed by Python Programming Language
  - Alerting
    - User can create own rules with aggregation in yaml files
    - User written rules are converted to Elasticsearch Queries
    - Implemented Multi-Theading where number of threads depends on number of devices Integrated
    - output will be shown in command line Interface
  - Reporting
    - User can create own rules for reports in yaml files
    - It offers Daily, Weekly and Monthly Reports by setting timeframe parameter in yaml file
    - User can create own templates for reports
    - Templates available are word, ppt, csv and json
    - Generated reports are stored in the Folder named "Generated Reports"
  - Health Check
    - Health Check is only applicable for Logstash
    - It will check the status of CPU Usage, JVM Statistics, Pipelines Connected and Pipeline Information
  <br/>
  Brief documentation is available in <a href="https://github.com/srinivas946/PyAlert/wiki">Wiki</a> page.
