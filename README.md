
# Distributed DNS-Like Name Resolution System

## Overview
A simplified DNS-like name resolution system using UDP sockets and Software-Defined Networking (SDN). An SDN controller dynamically manages packet forwarding in a Mininet network.

## Technologies Used
- Python 3
- UDP sockets
- Mininet
- Open vSwitch
- OpenFlow 1.3
- OS-Ken SDN controller
- Git and GitHub

## Project Structure
```text
distributed-dns/
├── controller/
│   ├── __init__.py
│   └── sdn_controller.py
├── src/
│   ├── dns_client.py
│   └── dns_server.py
├── topology/
│   └── topology.py
└── README.md
```

## Network Topology
- h1: DNS client — 10.0.0.1
- h2: DNS server 1 — 10.0.0.2
- h3: DNS server 2 — 10.0.0.3
- s1: OpenFlow 1.3 switch
- c0: Remote SDN controller

## Current DNS Records
| Hostname | Resolved IP |
|---|---|
| web.project.local | 10.0.0.10 |
| db.project.local | 10.0.0.20 |

## Requirements
- Ubuntu / WSL2
- Python 3
- Mininet
- Open vSwitch
- OS-Ken installed in the `osken311-venv` virtual environment

## Running the Project
Start the SDN controller in one terminal:

```bash
cd ~/distributed-dns
source ~/osken311-venv/bin/activate
PYTHONPATH="$HOME/distributed-dns" osken-manager controller.sdn_controller
```

Start the Mininet topology in another terminal:

```bash
cd ~/distributed-dns
sudo python3 topology/topology.py
```

Inside the Mininet CLI, start DNS servers:

```text
mininet> h2 python3 /home/mdtan/distributed-dns/src/dns_server.py --port 5353 &
mininet> h3 python3 /home/mdtan/distributed-dns/src/dns_server.py --port 5353 &
```

Test DNS resolution from h1:

```text
mininet> h1 python3 /home/mdtan/distributed-dns/src/dns_client.py web.project.local --server 10.0.0.2 --port 5353
mininet> h1 python3 /home/mdtan/distributed-dns/src/dns_client.py db.project.local --server 10.0.0.3 --port 5353
```

## Team Collaboration
The project is maintained collaboratively using Git and GitHub.

## Disclaimer
This is an educational prototype, not a replacement for production DNS.
