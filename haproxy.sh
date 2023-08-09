#!/bin/bash

apt-get update -y

apt-get upgrade -y

apt install haproxy -y

systemctl enable haproxy

ufw disable

wget -O /etc/haproxy/haproxy.cfg https://raw.githubusercontent.com/j-bothma/haproxy/main/haproxy.cfg

mkdir /etc/certs

wget -O /etc/certs/cert.pem.rsa https://raw.githubusercontent.com/j-bothma/haproxy/main/cert.pem.rsa

wget -O /etc/certs/cert.pem.ecdsa https://raw.githubusercontent.com/j-bothma/haproxy/main/cert.pem.ecdsa

wget -O /etc/haproxy/path.map https://raw.githubusercontent.com/j-bothma/haproxy/main/path.map

systemctl start haproxy
