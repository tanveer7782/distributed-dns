
import argparse
import socket
import json

DNS_RECORDS = {
    "web.project.local": "10.0.0.10",
    "db.project.local": "10.0.0.20",
    "files.project.local": "10.0.0.30",
}


def main():
    parser = argparse.ArgumentParser(description="UDP DNS-like server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5353)
    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((args.host, args.port))

    print(f"DNS-like server listening on {args.host}:{args.port}")

    while True:
        data, client_address = server.recvfrom(2048)

        try:
            request = json.loads(data.decode("utf-8"))
            hostname = request.get("hostname", "").strip().lower()

            response = {
                "hostname": hostname,
                "ip": DNS_RECORDS.get(hostname),
                "server": args.host,
                "status": (
                    "OK" if hostname in DNS_RECORDS else "NOT_FOUND"
                ),
            }

            server.sendto(
                json.dumps(response).encode("utf-8"),
                client_address,
            )
            print(f"{client_address} requested {hostname}: {response['status']}")

        except (json.JSONDecodeError, UnicodeDecodeError):
            server.sendto(
                json.dumps({
                    "status": "BAD_REQUEST",
                    "message": "Send a JSON request containing hostname",
                }).encode("utf-8"),
                client_address,
            )


if __name__ == "__main__":
    main()
