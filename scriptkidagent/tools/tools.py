import re
import subprocess
import time
import os
from typing import Any
from pwn import *

from agentlib.lib import tools


def clean_ansi_sequences(text):
    ansi_pattern = r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
    clean_text = re.sub(ansi_pattern, "", text)
    return clean_text


def read_output(process, timeout=20):
    """
    Args:
        process (process): The msfconsole process.
        timeout:

    Returns:

    """
    output = ""
    is_blocked = False
    while True:
        if process.can_recv():
            output += process.recv(1024).decode("utf-8")
        else:
            time.sleep(1)
            timeout -= 1
        if output.endswith("$ ") or output.endswith("# ") or output.endswith("> "):
            break
        if timeout <= 0:
            is_blocked = True
            break
    # if there are control characters in the last line of output, remove them
    last_line = output.split("\n")[-1]
    if last_line:
        output = output[: -len(last_line)]
        # remove all ANSI escape sequences
        last_line = clean_ansi_sequences(last_line)
        # remove all control characters
        last_line = "".join([i for i in last_line if i.isprintable()])
        # extract the last line
        # patterns = ["msf6", "exploit\([^)]*\)", "> "]
        # pattern = "|".join(patterns)
        # matches = re.findall(pattern, last_line)

        # last_line = " ".join(matches)
        output += last_line
    return output, is_blocked


def execute_in_msfconsole(process, command: str, timeout=20) -> tuple[str | Any, bool]:
    """
    Executes a command in msfconsole and returns the result.

    Args:
        process (process): The msfconsole process.
        command (str): The command to execute in msfconsole.
        timeout (int): The timeout for the command.

    Returns:
        str: The output of the command.
        bool: Whether the command is blocked.

    """
    # this should be painful as we need to interact with a console with tty
    process.sendline(command)
    output, is_blocked = read_output(process, timeout=timeout)
    return output, is_blocked

@tools.tool
def execute_cmds_in_msfconsole(commands: list[str], timeout=20) -> str:
    """
    Executes a list of commands in msfconsole and returns the result. Note that this command is stateless and will not be able to interact with the previous msfconsole session.
    
    Args:
        command (str): The command to execute in msfconsole.
        
    Returns:
        str: The output of the command.
    """
    # this should be painful as we need to interact with a console with tty
    io = process(["msfconsole", "-q", "--no-readline"],
                               env={"HOME": os.environ['HOME'], "TERM": "dumb"})
    io.recvuntil(b'> ')
    output = ""
    for command in commands:
        io.sendline(command)
        output, _ = read_output(io, timeout=timeout)
    io.close()
    return output


@tools.tool
def execute_in_bash(command: str) -> str:
    """
    Run a shell command and return the output. The output will be truncated, so if you are expecting a lot of output please pipe the results into a file which can be passed onto the next step by appending | tee /tmp/some_file.txt to the command. You can later use grep to search for the output in the file.

    Args:
        command (str): The command to run

    Returns:
        str: The output of the command
    """
    try:
        p = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        try:
            stdout, stderr = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()  # Kill the process if timeout expires
            try:
                stdout, stderr = p.communicate(
                    timeout=5
                )  # Collect any remaining output
                stdout += b"\nThe process was killed because it took too long to run, the output may be incomplete."
                stderr += b"\nThe process was killed because it took too long to run, the output may be incomplete."
            except subprocess.TimeoutExpired:
                stdout, stderr = (
                    b"The process hangs, no stdout",
                    b"The process hangs, no stderr",
                )
        try:
            stdout = stdout.decode("utf-8").strip()
        except UnicodeDecodeError:
            stdout = stdout.decode("latin-1").strip()
        try:
            stderr = stderr.decode("utf-8").strip()
        except UnicodeDecodeError:
            stderr = stderr.decode("latin-1").strip()
        exit_code = p.returncode
        output = f"# Running Command `{command}`:\nExit Code: {exit_code}\n"
        MAX_OUT_LEN = 4096
        if stdout:
            if len(stdout) > MAX_OUT_LEN:
                stdout = stdout[:MAX_OUT_LEN] + "\n<Stdout Output truncated>\n"
            if len(stdout) > 4096:
                # TODO give it better tools for this
                output += "Note: If the output is cut off, you will need to grep the output file to search for matches. Please make your grep as inclusive as possible to allow for fuzzy matches.\n"
            output += f"##Stdout\n```\n{stdout}\n```\n"
        else:
            output += "##Stdout\n```\n<No Stdout Output>\n```\n"
        if stderr:
            if len(stderr) > MAX_OUT_LEN:
                stderr = stderr[:MAX_OUT_LEN] + "\n<Stderr Output truncated>"
            output += f"##Stderr\n```\n{stderr}\n```\n"

        return output
    except Exception as e:
        return f"Error running command: {e}"
