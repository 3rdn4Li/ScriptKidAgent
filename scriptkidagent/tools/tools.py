import re
import subprocess
import time
from typing import Any

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



from openhands.agenthub.browsing_agent.browsing_agent import BrowsingAgent
from openhands.core.config.agent_config import AgentConfig
from openhands.controller.state.state import State
from openhands.runtime.browser import browse
from openhands.runtime.browser.browser_env import BrowserEnv
from openhands.events.action import BrowseInteractiveAction, MessageAction, AgentFinishAction
from openai import OpenAI
import asyncio
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_API_BASE'])

# Define the model to use
model_name = "gpt-4o"

config = AgentConfig(
    codeact_enable_browsing=True,
    codeact_enable_llm_editor=False,
    codeact_enable_jupyter=True,
    micro_agent_name=None,
    memory_enabled=False,
    memory_max_threads=3,
    llm_config=None,
    use_microagents=True,
    disabled_microagents=None,
)


# Define a helper class or function for the LLM
class LLM:
    def __init__(self, model_name):
        self.model_name = model_name

    def completion(self, messages, stop=None):
        return client.chat.completions.create(model=self.model_name,
        messages=messages,
        stop=stop)

    @staticmethod
    def format_messages_for_llm(messages):
        # Handles Message objects
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    def reset(self):
        pass

# Initialize the LLM object
llm = LLM(model_name)

def summarize_result(state, ba):
    summary_requirement = MessageAction(content = "Since you have searched too many times, stop doing any web-related actions right now and summarize the result so far.")
    summary_requirement._source='user'
    state.history.append(summary_requirement)
    browser_action = ba.step(state)
    if isinstance(browser_action, BrowseInteractiveAction) and browser_action.browsergym_send_msg_to_user:
        print(browser_action.browsergym_send_msg_to_user)
        print("Reply to the user")
        return browser_action.browsergym_send_msg_to_user
    else:
        return "The searching agent has not found the answer."
    

@tools.tool
def search_in_web(task = "Search and tell me is what is CVE2024-38077?"):
    """

    Run a searching agent to search the web for the task and return the output.
    The task input can be any sentence, question, or command.

    Args:
        task (str): The task to run.

    Returns:
        str: The execution results of the task.
    """

    state = State()
    state.inputs['task'] = task
    ba = BrowsingAgent(llm=llm, config=config)
    browser_env = BrowserEnv()
    for i in range(20):
        browser_action = ba.step(state)
        if isinstance(browser_action, BrowseInteractiveAction) and browser_action.browsergym_send_msg_to_user:
            print(browser_action.browsergym_send_msg_to_user)
            print("Reply to the user")
            return browser_action.browsergym_send_msg_to_user
        print("browser action", browser_action)
        if isinstance(browser_action, BrowseInteractiveAction):
            browser_observation = browse(browser_action, browser_env)
            obs = asyncio.run(browser_observation)
            state.history.append(obs)
        elif isinstance(browser_action, MessageAction):
            print(browser_action.content)
            print("we are done with message")
            return summarize_result(state, ba)
        elif isinstance(browser_action, AgentFinishAction):
            print(browser_action.content)
            print("we are done with agent finish")
            return summarize_result(state, ba)
    print("run 20 times but not done")
    return summarize_result(state, ba)

