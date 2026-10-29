import json
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_SCRIPT = PROJECT_ROOT / "src" / "dns_server.py"


class DNSServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ask the operating system for an available UDP port.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("127.0.0.1", 0))
            cls.port = sock.getsockname()[1]

        cls.server = subprocess.Popen(
            [
                sys.executable,
                str(SERVER_SCRIPT),
                "--host", "127.0.0.1",
                "--port", str(cls.port),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait until the server is ready to receive requests.
        deadline = time.time() + 5
        while time.time() < deadline:
            if cls.server.poll() is not None:
                error = cls.server.stderr.read()
                raise RuntimeError(f"DNS server failed to start:\n{error}")

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.settimeout(0.2)
                    sock.sendto(
                        json.dumps(
                            {"hostname": "web.project.local"}
                        ).encode("utf-8"),
                        ("127.0.0.1", cls.port),
                    )
                    data, _ = sock.recvfrom(2048)
                    response = json.loads(data.decode("utf-8"))
                    if response.get("status") == "OK":
                        break
            except (socket.timeout, OSError, json.JSONDecodeError):
                time.sleep(0.1)
        else:
            cls.tearDownClass()
            raise RuntimeError("DNS server did not become ready in time")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "server") and cls.server.poll() is None:
            cls.server.terminate()
            try:
                cls.server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                cls.server.kill()
                cls.server.wait()

        if hasattr(cls, "server") and cls.server.stderr:
            cls.server.stderr.close()

    def query(self, hostname):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(2)
            request = {"hostname": hostname}
            sock.sendto(
                json.dumps(request).encode("utf-8"),
                ("127.0.0.1", self.port),
            )
            data, _ = sock.recvfrom(2048)
        return json.loads(data.decode("utf-8"))

    def test_web_hostname(self):
        response = self.query("web.project.local")
        self.assertEqual(response["status"], "OK")
        self.assertEqual(response["ip"], "10.0.0.10")

    def test_database_hostname(self):
        response = self.query("db.project.local")
        self.assertEqual(response["status"], "OK")
        self.assertEqual(response["ip"], "10.0.0.20")

    def test_files_hostname(self):
        response = self.query("files.project.local")
        self.assertEqual(response["status"], "OK")
        self.assertEqual(response["ip"], "10.0.0.30")

    def test_unknown_hostname(self):
        response = self.query("unknown.project.local")
        self.assertEqual(response["status"], "NOT_FOUND")
        self.assertIsNone(response["ip"])

    def test_hostname_lookup_is_case_insensitive(self):
        response = self.query("WEB.PROJECT.LOCAL")
        self.assertEqual(response["status"], "OK")
        self.assertEqual(response["ip"], "10.0.0.10")


if __name__ == "__main__":
    unittest.main(verbosity=2)
