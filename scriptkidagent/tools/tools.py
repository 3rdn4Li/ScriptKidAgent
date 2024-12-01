from pwn import *
import subprocess
from agentlib.lib import tools


def execute_in_msfconsole(process, command: str) -> str:
    """
    Executes a command in msfconsole and returns the result.

    Args:
        process (process): The msfconsole process.
        command (str): The command to execute in msfconsole.

    Returns:
        str: The result of the command execution.
    """
    # this should be painful as we need to interact with a console with tty
    process.sendline(command)
    process.expect('msf6 >')
    output = process.before
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
            command, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            stdout, stderr = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()  # Kill the process if timeout expires
            try:
                stdout, stderr = p.communicate(timeout=5)  # Collect any remaining output
                stdout += b'\nThe process was killed because it took too long to run, the output may be incomplete.'
                stderr += b'\nThe process was killed because it took too long to run, the output may be incomplete.'
            except subprocess.TimeoutExpired:
                stdout, stderr = b'The process hangs, no stdout', b'The process hangs, no stderr'
        try:
            stdout = stdout.decode('utf-8').strip()
        except UnicodeDecodeError:
            stdout = stdout.decode('latin-1').strip()
        try:
            stderr = stderr.decode('utf-8').strip()
        except UnicodeDecodeError:
            stderr = stderr.decode('latin-1').strip()
        exit_code = p.returncode
        output = f'# Running Command `{command}`:\nExit Code: {exit_code}\n'
        MAX_OUT_LEN = 4096
        if stdout:
            if len(stdout) > MAX_OUT_LEN:
                stdout = stdout[:MAX_OUT_LEN] + '\n<Stdout Output truncated>\n'
            if len(stdout) > 4096:
                # TODO give it better tools for this
                output += 'Note: If the output is cut off, you will need to grep the output file to search for matches. Please make your grep as inclusive as possible to allow for fuzzy matches.\n'
            output += f"##Stdout\n```\n{stdout}\n```\n"
        else:
            output += '##Stdout\n```\n<No Stdout Output>\n```\n'
        if stderr:
            if len(stderr) > MAX_OUT_LEN:
                stderr = stderr[:MAX_OUT_LEN] + '\n<Stderr Output truncated>'
            output += f"##Stderr\n```\n{stderr}\n```\n"

        return output
    except Exception as e:
        return f'Error running command: {e}'
