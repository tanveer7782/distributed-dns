# Distributed DNS-Like Name Resolution System

A simplified DNS-like name-resolution system built with Python UDP sockets,
Mininet, Open vSwitch, and an SDN controller using OS-Ken.

The project demonstrates hostname-to-IP resolution, handling of unknown
hostnames, a virtual network topology, OpenFlow rules, and controller-based
Ethernet MAC learning.

## 1. Project Objectives

- Resolve hostnames using a simplified DNS-like UDP protocol.
- Run two DNS servers in a Mininet network.
- Return `OK` for known hostnames and `NOT_FOUND` for unknown hostnames.
- Use Open vSwitch with OpenFlow 1.3.
- Install an OpenFlow rule automatically for IPv4 UDP traffic destined for
  port 5353.
- Observe DNS-like requests through SDN controller logs.

## 2. Technologies Used

- Python 3
- UDP sockets
- Mininet
- Open vSwitch (OVS)
- OS-Ken SDN controller
- OpenFlow 1.3
- Ubuntu / WSL2
- Git and GitHub

## 3. Project Architecture

The Mininet topology contains three hosts connected to one Open vSwitch:

```text
                    SDN Controller
                       OS-Ken
                         |
                    OpenFlow 1.3
                         |
                    +----------+
                    |   s1     |
                    |   OVS    |
                    +----------+
                    /    |     \
                   /     |      \
                h1       h2      h3
              Client    DNS 1   DNS 2
             10.0.0.1 10.0.0.2 10.0.0.3
```

Example hostname mappings:

| Hostname | DNS server | Resolved IP |
|---|---|---|
| `web.project.local` | `10.0.0.2` | `10.0.0.10` |
| `db.project.local` | `10.0.0.3` | `10.0.0.20` |
| `unknown.project.local` | `10.0.0.2` | Not found |

The DNS servers listen on UDP port `5353`.

### How it works

1. The client sends a hostname-resolution request to a selected DNS server.
2. The Open vSwitch applies its OpenFlow rules to network packets.
3. The controller installs a priority-10 rule for IPv4 UDP traffic
   destined for port 5353.
4. The controller logs matching DNS-like requests and uses MAC learning
   to forward Ethernet packets.
5. The DNS server returns the resolved IP address or `NOT_FOUND`.

Note: The controller currently uses MAC learning for forwarding. The
DNS-specific rule sends matching traffic to the controller; it does not
yet implement hostname-based DNS server selection.

## 4. Repository Structure

```text
distributed-dns/
├── controller/
│   ├── __init__.py
│   └── sdn_controller.py
├── docs/
├── src/
│   ├── dns_client.py
│   └── dns_server.py
├── tests/
├── topology/
│   └── topology.py
├── .gitignore
└── README.md
```

## 5. Requirements

Use Ubuntu or Ubuntu under WSL2 with VS Code connected to WSL.

Install the required system packages:

```bash
sudo apt update
sudo apt install -y mininet openvswitch-switch git python3-pip python3-venv
```

Verify the installations:

```bash
mn --version
ovs-vsctl --version
python3 --version
git --version
```

### Set up OS-Ken

If OS-Ken is not already installed in your environment:

```bash
python3 -m venv ~/osken311-venv
source ~/osken311-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install os-ken
```

If the virtual environment already exists, activate it instead of creating
it again:

```bash
source ~/osken311-venv/bin/activate
```

Confirm the controller launcher is available:

```bash
osken-manager --help
```

## 6. Running the Project

Use separate VS Code terminal windows for the controller and Mininet.

### Terminal 1: Start the SDN controller

```bash
cd ~/distributed-dns
source ~/osken311-venv/bin/activate
PYTHONPATH="$HOME/distributed-dns" osken-manager controller.sdn_controller
```

Keep this terminal running. The controller should load the application
and wait for the switch to connect.

### Terminal 2: Start the Mininet topology

```bash
cd ~/distributed-dns
sudo python3 topology/topology.py
```

Wait for the `mininet>` prompt.

### Start DNS server 1

At the `mininet>` prompt, run:

```text
h2 python3 /home/YOUR_USERNAME/distributed-dns/src/dns_server.py --port 5353 &
```

### Start DNS server 2

```text
h3 python3 /home/YOUR_USERNAME/distributed-dns/src/dns_server.py --port 5353 &
```

Replace `YOUR_USERNAME` with your Ubuntu username. You can find it in a
normal Ubuntu terminal by running:

```bash
whoami
```

For example, if your Ubuntu home directory is `/home/mdtan`, use
`/home/mdtan/distributed-dns/...` in the Mininet commands.

## 7. Testing DNS Resolution

Run these commands at the `mininet>` prompt.

### Test 1: Resolve the web hostname

```text
h1 python3 /home/YOUR_USERNAME/distributed-dns/src/dns_client.py web.project.local --server 10.0.0.2 --port 5353
```

Expected result:

```text
Hostname: web.project.local
Status: OK
IP: 10.0.0.10
```

### Test 2: Resolve the database hostname

```text
h1 python3 /home/YOUR_USERNAME/distributed-dns/src/dns_client.py db.project.local --server 10.0.0.3 --port 5353
```

Expected result:

```text
Hostname: db.project.local
Status: OK
IP: 10.0.0.20
```

### Test 3: Test an unknown hostname

```text
h1 python3 /home/YOUR_USERNAME/distributed-dns/src/dns_client.py unknown.project.local --server 10.0.0.2 --port 5353
```

Expected result:

```text
Hostname: unknown.project.local
Status: NOT_FOUND
IP: Not found
```

Replace `YOUR_USERNAME` in these commands with your Ubuntu username.

## 8. Verify OpenFlow Rules

At the `mininet>` prompt, run:

```text
sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

Look for a rule similar to:

```text
priority=10,udp,tp_dst=5353 actions=CONTROLLER:65535
```

The exact output format may vary. This rule should be installed automatically
when the switch connects to the controller.

The controller terminal should also show messages similar to:

```text
Installed DNS UDP/5353 controller rule on switch 1
Switch connected: 1
DNS-like UDP request: 10.0.0.1 -> 10.0.0.2, port 5353
```

## 9. Basic Network Connectivity Test

At the `mininet>` prompt:

```text
pingall
```

Expected result: all three Mininet hosts can reach one another, with
`0% dropped` under normal conditions.

## 10. Troubleshooting

### Mininet reports stale network state

Exit the Mininet CLI and run this in a normal Ubuntu terminal:

```bash
sudo mn -c
```

Then restart the controller and topology.

### Controller does not start

Activate the correct virtual environment:

```bash
source ~/osken311-venv/bin/activate
osken-manager --help
```

Make sure the controller terminal remains open while Mininet runs.

### DNS client times out

- Confirm both DNS servers were started successfully.
- Check the hostname, server IP, and UDP port.
- Confirm that the controller and Mininet are running.
- Check the controller terminal for DNS-like request logs.
- Verify that the OpenFlow rules are installed.

### Python syntax check

Run this in a normal Ubuntu terminal:

```bash
cd ~/distributed-dns
python3 -m py_compile controller/sdn_controller.py
python3 -m py_compile src/dns_client.py src/dns_server.py
python3 -m py_compile topology/topology.py
```

No output means the syntax checks passed.

## 11. Team Responsibilities

Suggested division for a four-member team:

| Member | Responsibility |
|---|---|
| Member 1 | UDP client implementation and request/response testing |
| Member 2 | DNS server implementation and hostname-to-IP mapping |
| Member 3 | SDN controller, OpenFlow rules, and MAC-learning logic |
| Member 4 | Mininet topology, integration, documentation, and demo coordination |

All members should review the integrated code, run the tests, and understand
the complete request flow before the demonstration.

## 12. GitHub Collaboration

Repository:
https://github.com/tanveer7782/distributed-dns

Clone the project:

```bash
git clone https://github.com/tanveer7782/distributed-dns.git
cd distributed-dns
```

Before starting work, pull the latest changes:

```bash
git pull origin main
```

After making changes:

```bash
git add .
git commit -m "Describe your changes"
git push
```

Avoid committing virtual environments, Python cache files, or generated
temporary files.

## 13. Current Project Status

Verified during development:

- Mininet topology starts successfully.
- The three-host network passes `pingall`.
- Both known hostnames resolve to their expected IP addresses.
- An unknown hostname returns `NOT_FOUND`.
- The controller automatically installs the UDP/5353 OpenFlow rule.
- The controller logs DNS-like UDP requests.
- The updated controller has been pushed to GitHub.

## 14. Future Improvements

- Add automated unit and integration tests.
- Implement hostname-aware server selection in the SDN controller.
- Add request timeouts and improved error handling.
- Record test results and network measurements.
- Add diagrams and screenshots to the project documentation.

---

**Project:** Distributed DNS-Like Name Resolution System  
**Networking:** UDP sockets, Mininet, Open vSwitch, OpenFlow 1.3  
**Controller:** OS-Ken
