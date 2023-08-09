#!/bin/bash

apt-get update

apt-get upgrade

apt install haproxy

systemctl enable haproxy

ufw disable

wget -O /etc/haproxy/haproxy.cfg https://raw.githubusercontent.com/j-bothma/haproxy/main/haproxy.cfg

mkdir /home/ubuntu/certs/

wget -O /home/ubuntu/certs/cert.pem.rsa https://raw.githubusercontent.com/j-bothma/haproxy/main/cert.pem.rsa

wget -O /home/ubuntu/certs/cert.pem.ecdsa https://raw.githubusercontent.com/j-bothma/haproxy/main/cert.pem.ecdsa

systemctl start haprxy
