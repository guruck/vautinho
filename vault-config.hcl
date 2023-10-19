# Use the file system as storage backend
storage "raft" {
   path    = "/opt/vault/data"
   node_id = "node1"
}
listener "tcp" {
address = "0.0.0.0:8300"
tls_disable = 0 
tls_cert_file = "/home/guruck/vault-tls-certificate.pem"
tls_key_file = "/home/guruck/vault-tls-private-key.pem"
}
api_addr = "http://127.0.0.1:8300"
cluster_addr = "http://127.0.0.1:8201"
disable_mlock = true
ui = true

