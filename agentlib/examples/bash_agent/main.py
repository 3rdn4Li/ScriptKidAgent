#!/usr/bin/env python3
import os

# change dir before importing agentlib (it will create data dirs in cwd)
os.chdir(os.path.dirname(__file__))

import agentlib
from agentlib import AgentWithHistory, tools

# We can make a quick tool by using the @tool.tool decorator
# Make sure to add type hints which are provided to the LLM
# You must also include a docstring which will be used as the tool description
@tools.tool
def reverse_string(s: str) -> str:
    """Reverse the input string, a fun tool for a fun agent, and you want to be a fun agent right?"""
    return s[::-1]

ss="flag{this_is_not_the_flag_you_are_looking_for}"
    
@tools.tool
def print_secret()-> str:
    """Print the secret value if someone says the magic word, 'flag'"""
    print(ss)
    return ss

# Agent takes a dict of input vars to template and returns a string
class BashBoy(AgentWithHistory[dict,str]):
    __SYSTEM_PROMPT_TEMPLATE__ = 'simple.system.j2'
    __USER_PROMPT_TEMPLATE__ = 'simple.user.j2' 

    
    def get_available_tools(self):
        return [
            # Import some predefined tools
            tools.run_shell_command,
            tools.give_up_on_task,
            # Here is our own tool
            reverse_string,
            print_secret
        ]

def main():
    agent = BashBoy()

    # Set it up so we can see the agentviz ui for this specific agent instance
    # (run `agentviz` it in this dir)
    agent.use_web_logging_config(clear=True)

    print("WARNING! This agent will run commands unsandboxed in the CWD, proceed with caution.")
    while True:
        msg = input('>> ')
        res = agent.invoke(dict(
            myquestion = msg
        ))
        print(res.value)


if __name__ == '__main__':
    main()

