
import argparse
import json
import socket


def main():
    parser = argparse.ArgumentParser(description="UDP DNS-like client")
    parser.add_argument("hostname", help="Hostname to resolve")
    parser.add_argument("--server", default="10.0.0.2",
                        help="DNS server IP address")
    parser.add_argument("--port", type=int, default=5353)
    args = parser.parse_args()

    request = {"hostname": args.hostname.lower()}

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(3)

        client.sendto(
            json.dumps(request).encode("utf-8"),
            (args.server, args.port),
        )

        try:
            data, _ = client.recvfrom(2048)
            response = json.loads(data.decode("utf-8"))

            print(f"Hostname: {response.get('hostname', args.hostname)}")
            print(f"Status:   {response.get('status')}")

            if response.get("ip"):
                print(f"IP:       {response['ip']}")
            else:
                print("IP:       Not found")

            print(f"Response: {response}")

        except socket.timeout:
            print("Request timed out: DNS server did not respond.")
            raise SystemExit(1)


if __name__ == "__main__":
    main()
