import re
from agentlib import AgentWithHistory, LLMFunction
from pathlib import Path
from typing import Dict
from scriptkidagent.tools.tools import execute_in_bash
from agentlib.lib.common.parsers import BaseParser


class VulnReportParser(BaseParser):
    pass


class IdentifyVulnAgent(AgentWithHistory[dict,str]):
    pass