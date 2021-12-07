# Configure Cluster Apache Kafka

Our cluster will consist of 3 servers containing Oracle Linux 7.9 containing 2 CPU and 2GB Ram.

**Hostnames**

*IP's addresses can change depending on your network.*

    kafka001.local  -> 192.168.1.11

    kafka002.local  -> 192.168.1.12

    kafka003.local  -> 192.168.1.13

```sh
cat << EOF | sudo tee -a /etc/hosts
192.168.1.11    kafka001.local
192.168.1.12    kafka002.local
192.168.1.13    kafka003.local
EOF
```

**Disable Firewall**

```sh
sudo systemctl stop firewalld
sudo systemctl disable firewalld
```

**Install OpenJDK 1.8**

```sh
sudo yum install -y java-1.8.0-openjdk.x86_64
```

**Disable SELinux**

```sh
sudo sed -i 's/^SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
sudo setenforce 0
sudo reboot 
```

**Create kafka user**
```sh
sudo useradd -r -M -s /bin/false kafka
```

**Install Kafka**

```sh
cd /tmp/
# Download
curl -sfLO https://dlcdn.apache.org/kafka/3.0.0/kafka_2.12-3.0.0.tgz

# Untar
tar -xzf kafka_2.12-3.0.0.tgz

# Rename Kafka directory
sudo mv kafka_2.12-3.0.0 /var/lib/kafka

# Create Zookeeper data directory
sudo mkdir -p /var/lib/zookeeper/data

# Create Kafka topics storage directory
sudo mkdir -p /var/lib/kafka/data/

```

**Zookeeper configuration**

```sh
# Define data directory
sudo sed -i 's/^dataDir=.*/dataDir=\/var\/lib\/zookeeper\/data/g' /var/lib/kafka/config/zookeeper.properties
    
# Define cluster servers address
sudo echo "server.1=kafka001.local:2888:3888" >> /var/lib/kafka/config/zookeeper.properties
sudo echo "server.2=kafka002.local:2888:3888" >> /var/lib/kafka/config/zookeeper.properties
sudo echo "server.3=kafka003.local:2888:3888" >> /var/lib/kafka/config/zookeeper.properties

# Other configurations (https://zookeeper.apache.org/doc/r3.1.2/zookeeperStarted.html)
sudo echo "initLimit=5" >> /var/lib/kafka/config/zookeeper.properties
sudo echo "syncLimit=2" >> /var/lib/kafka/config/zookeeper.properties
```

**Define ID Node**

Zookeeper will identify each node by the value it contains in the file: /var/lib/zookeeper/data/myid

For this, each cluster node must contain its unique ID.

```sh
#Node kafka001.local
echo "1" | sudo tee /var/lib/zookeeper/data/myid
```

```sh
#Node kafka002.local
echo "2" | sudo tee /var/lib/zookeeper/data/myid
```

```sh
#Node kafka003.local
echo "3" | sudo tee /var/lib/zookeeper/data/myid
```

**Kafka configuration**

```sh
#Node kafka001.local
sudo sed -i 's/^broker.id=.*/broker.id=1/g' /var/lib/kafka/config/server.properties
sudo sed -i "s/^#listeners=.*/listeners=PLAINTEXT:\/\/kafka001.local:9092/g" /var/lib/kafka/config/server.properties
sudo sed -i "s/^#advertised.listeners=.*/advertised.listeners=PLAINTEXT:\/\/kafka001.local:9092/g" /var/lib/kafka/config/server.properties
```

```sh
#Node kafka002.local
sudo sed -i 's/^broker.id=.*/broker.id=2/g' /var/lib/kafka/config/server.properties
sudo sed -i "s/^#listeners=.*/listeners=PLAINTEXT:\/\/kafka002.local:9092/g" /var/lib/kafka/config/server.properties
sudo sed -i "s/^#advertised.listeners=.*/advertised.listeners=PLAINTEXT:\/\/kafka002.local:9092/g" /var/lib/kafka/config/server.properties
```

```sh
#Node kafka003.local
sudo sed -i 's/^broker.id=.*/broker.id=3/g' /var/lib/kafka/config/server.properties
sudo sed -i "s/^#listeners=.*/listeners=PLAINTEXT:\/\/kafka003.local:9092/g" /var/lib/kafka/config/server.properties
sudo sed -i "s/^#advertised.listeners=.*/advertised.listeners=PLAINTEXT:\/\/kafka003.local:9092/g" /var/lib/kafka/config/server.properties
```


*There is **log.dirs** property to contain the path where **topics** will be stored.*

```sh
sudo sed -i 's/^log.dirs=.*/log.dirs=\/var\/lib\/kafka\/data/g' /var/lib/kafka/config/server.properties
sudo sed -i 's/^zookeeper.connect=.*/zookeeper.connect=kafka001.local:2181,kafka002.local:2181,kafka003.local:2181/g' /var/lib/kafka/config/server.properties
```

*If your environments is **Staging** enable delete topic*

```sh
sudo echo "delete.topic.enable=true" >> /var/lib/kafka/config/server.properties
```

**Change owner to kafka user**
```sh
# Change owner
sudo chown -R kafka. /var/lib/zookeeper
sudo chown -R kafka. /var/lib/kafka
```

**Create Zookeeper systemd service**

```sh
cat << EOF | sudo tee /etc/systemd/system/zookeeper.service
[Unit]
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
User=kafka
ExecStart=/var/lib/kafka/bin/zookeeper-server-start.sh /var/lib/kafka/config/zookeeper.properties
ExecStop=/var/lib/kafka/bin/zookeeper-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF
```

```sh
sudo systemctl enable zookeeper.service
sudo systemctl start zookeeper.service
```


**Create Zookeeper systemd service**

```sh
cat << EOF | sudo tee /etc/systemd/system/kafka.service
[Unit]
Requires=zookeeper.service
After=network.target zookeeper.service

[Service]
Type=simple
User=kafka
ExecStart=/bin/sh -c '/var/lib/kafka/bin/kafka-server-start.sh /var/lib/kafka/config/server.properties'
ExecStop=/var/lib/kafka/bin/kafka-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF
```

```sh
sudo systemctl enable kafka.service
sudo systemctl start kafka.service
```

# Deploy aditional stack

Additional stack consisting of consumer, producer and UI for Kafka using Docker and Docker-compose 

**Run aditional stack**
```sh
docker-compose up --build --force-recreate -d
```
