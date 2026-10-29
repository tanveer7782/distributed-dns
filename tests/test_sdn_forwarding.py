import subprocess
import unittest


class SDNForwardingTests(unittest.TestCase):
    def test_dns_rule_is_installed(self):
        result = subprocess.run(
            [
                "sudo",
                "ovs-ofctl",
                "-O",
                "OpenFlow13",
                "dump-flows",
                "s1",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        flows = result.stdout

        self.assertIn("udp", flows)
        self.assertIn("tp_dst=5353", flows)
        self.assertIn("priority=10", flows)

    def test_controller_receives_dns_rule(self):
        result = subprocess.run(
            [
                "sudo",
                "ovs-ofctl",
                "-O",
                "OpenFlow13",
                "dump-flows",
                "s1",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("actions=CONTROLLER", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
