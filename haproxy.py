import requests
from requests.auth import HTTPBasicAuth

print("Please enter the <hostname>:<port> of the Haproxy instance:")
url = input()+"/v2"

print("Please enter the username:")
username = input()

print("Please enter the password:")
password = input()

basic = HTTPBasicAuth(username, password)

# Get config version
response = requests.get(url+"/services/haproxy/configuration/version", auth=basic)
print("version received")
version = str(response.json())

#Get config transaction ID
response = requests.post(url+f"/services/haproxy/transactions?version={version}", auth=basic)
print("transaction id received")
id = response.json()["id"]


#Create Backend

data = {
   "balance":
      { "algorithm":"leastconn" },
      "mode":"http",
      "name":"api_backend"
}

response = requests.post(url+f"/services/haproxy/configuration/backends?transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())
#Add servers
data = {
   "address":"ec2-3-92-61-237.compute-1.amazonaws.com",
   "check":"enabled",
   "name":"server1",
   "port":80,
}

response = requests.post(url+f"/services/haproxy/configuration/servers?backend=api_backend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

data = {
   "address":"ec2-44-210-116-255.compute-1.amazonaws.com",
   "check":"enabled",
   "name":"server2",
   "port":80,
}

response = requests.post(url+f"/services/haproxy/configuration/servers?backend=api_backend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

#Create Frontend
data={
    "default_backend": "api_backend",
  "maxconn": 2000,
  "name": "api_frontend",
  "mode": "http",
  "stick_table":{
      "expire": 60,
      "size": 5000,
      "type": "ip",
      "store": "http_req_rate(60s)"

  }
}


response = requests.post(url+f"/services/haproxy/configuration/frontends?transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

#Create Bind Addresses
# port 80
data = {
    
   "address":"*",
   "name":"http",
   "port":80

}

response = requests.post(url+f"/services/haproxy/configuration/binds?frontend=api_frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

#port 443
data = {
    
   "address":"*",
   "name":"https",
   "port":443,
   "ssl": True,
   "ssl_certificate": "/etc/certs/cert.pem",
   "ssl_min_ver": "TLSv1.2"
}

response = requests.post(url+f"/services/haproxy/configuration/binds?frontend=api_frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

#Add ACLs to fronend
data = {
  "acl_name": "secure_path",
  "criterion": "path_beg,url_dec",
  "index": 0,
  "value": "/secure"
}
response = requests.post(url+f"/services/haproxy/configuration/acls?parent_name=api_frontend&parent_type=frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

data = {
  "acl_name": "secure_conn",
  "criterion": "ssl_fc",
  "index": 1,
  "value": " "
}
response = requests.post(url+f"/services/haproxy/configuration/acls?parent_name=api_frontend&parent_type=frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

data = {
  "acl_name": "attack",
  "criterion": "path_beg,url_dec",
  "index": 2,
  "value": "/attack"
}
response = requests.post(url+f"/services/haproxy/configuration/acls?parent_name=api_frontend&parent_type=frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

data = {
  "acl_name": "map_path",
  "criterion": "path_beg,url_dec",
  "index": 3,
  "value": "/management /support /data"
}
response = requests.post(url+f"/services/haproxy/configuration/acls?parent_name=api_frontend&parent_type=frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

#Create HTTP Request rules

data = {
  "cond": "if",
  "cond_test": "secure_path !secure_conn",
  "redir_type": "scheme",
  "redir_value": "https",
  "index": 0,
  "type": "redirect"
}
response = requests.post(url+f"/services/haproxy/configuration/http_request_rules?parent_name=api_frontend&parent_type=frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

data = {
  "track-sc0-key": "src",
  "index": 1,
  "type": "track-sc0" 
}

response = requests.post(url+f"/services/haproxy/configuration/http_request_rules?parent_name=api_frontend&parent_type=frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

data = {
  "cond": "if",
  "cond_test": "{ sc_http_req_rate(0) gt 10 }",
  "deny_status": 429,
  "index": 2,
  "type": "deny"
}
response = requests.post(url+f"/services/haproxy/configuration/http_request_rules?parent_name=api_frontend&parent_type=frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

data = {
  "cond": "if",
  "cond_test": "attack",
  "index": 3,
  "type": "deny"
}
response = requests.post(url+f"/services/haproxy/configuration/http_request_rules?parent_name=api_frontend&parent_type=frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())

data = {
  "cond": "if",
  "cond_test": "map_path",
  "path_fmt": "%[path,lower,map_beg(/etc/haproxy/path.map)]",
  "index": 4,
  "type": "set-path"
}
response = requests.post(url+f"/services/haproxy/configuration/http_request_rules?parent_name=api_frontend&parent_type=frontend&transaction_id={id}", auth=basic, headers={"Content-Type": "application/json"}, json=data)
print(response.json())



#Close transaction
commit = requests.put(url+f"/services/haproxy/transactions/{id}", auth=basic)

print(commit.json())

