from openhands.agenthub.browsing_agent.browsing_agent import BrowsingAgent
from openhands.core.config.agent_config import AgentConfig
from openhands.controller.state.state import State
from openhands.runtime.browser import browse
from openhands.runtime.browser.browser_env import BrowserEnv
from openhands.events.action import BrowseInteractiveAction, MessageAction, AgentFinishAction
from openai import OpenAI
import asyncio

# Set your API key
api_key = "sk-Q1K19zjR5Ld-MPi_6-TpmA"
base_url = "http://128.111.49.59:4000"

client = OpenAI(api_key=api_key, base_url=base_url)

# Define the model to use
model_name = "oai-gpt-4o"

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


def search_in_web(task = "Search and tell me is what is CVE2024-38077?"):

    state = State()
    ba = BrowsingAgent(llm=llm, config=config)
    state.inputs['task'] = task


    browser_env = BrowserEnv()
    for i in range(50):
        browser_action = ba.step(state)
        if browser_action.browsergym_send_msg_to_user:
            print(browser_action.browsergym_send_msg_to_user)
            print("SUCCESS!")
            exit()
        print("browser action", browser_action)
        if isinstance(browser_action, BrowseInteractiveAction):
            browser_observation = browse(browser_action, browser_env)
            obs = asyncio.run(browser_observation)
            state.history.append(obs)
        elif isinstance(browser_action, MessageAction):
            print(browser_action.content)
            print("we are done with message")
            exit()
        elif isinstance(browser_action, AgentFinishAction):
            print(browser_action.content)
            print("we are done with agent finish")
            exit()
    print("run 50 times but not done")
