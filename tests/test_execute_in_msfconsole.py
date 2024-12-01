import unittest
import os
from unittest.mock import Mock, patch

from pwnlib.tubes.process import process

from scriptkidagent.tools.tools import execute_in_msfconsole


class TestMsfConsoleExecution(unittest.TestCase):
    def setUp(self):
        self.mock_process = Mock()
        self.mock_process.sendline = Mock()
        self.mock_process.recvuntil = Mock()
        self.mock_process.recv = Mock()

    @patch("pwn.process")
    def test_execute_command_success(self, mock_pwntools_process):
        self.process = process(
            ["msfconsole", "-q", "--no-readline"],
            env={"HOME": os.environ["HOME"], "TERM": "dumb"},
        )  # TODO: refine the args
        self.process.recvuntil("> ")

        # 执行测试
        result = execute_in_msfconsole(self.mock_process, "test_command")

        # 验证结果
        self.assertIn("Command executed successfully", result)
        self.assertIn("Result data", result)

        # 验证是否正确调用了 pwntools 的方法
        self.mock_process.sendline.assert_called_once_with("test_command")
        self.mock_process.recvuntil.assert_called_with(b"msf6 > ")

    def test_execute_command_timeout(self):
        # 模拟 recvuntil 超时
        self.mock_process.recvuntil.side_effect = TimeoutError(
            "Timeout waiting for prompt"
        )

        # 验证超时异常是否被正确抛出
        with self.assertRaises(TimeoutError):
            execute_in_msfconsole(self.mock_process, "test_command")

    def test_execute_command_error(self):
        # 设置模拟进程返回错误信息
        prompt = b"msf6 > "
        error_output = b"[-] Error: Command failed\nmsf6 > "

        self.mock_process.recvuntil.return_value = prompt
        self.mock_process.recv.return_value = error_output

        # 执行测试
        result = execute_in_msfconsole(self.mock_process, "invalid_command")

        # 验证错误信息是否在结果中
        self.assertIn("Error: Command failed", result)

    def test_invalid_process(self):
        # 测试无效的进程对象
        with self.assertRaises(AttributeError):
            execute_in_msfconsole(None, "test_command")

    def tearDown(self):
        # 清理测试环境
        self.mock_process = None
