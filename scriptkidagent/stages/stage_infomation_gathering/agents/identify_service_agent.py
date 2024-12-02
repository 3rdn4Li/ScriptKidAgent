import re
from agentlib import AgentWithHistory, LLMFunction
from pathlib import Path
from typing import Dict
from scriptkidagent.tools.tools import execute_in_bash
from agentlib.lib.common.parsers import BaseParser

TOOLS = {"execute_in_bash": execute_in_bash}


class ServiceReportParser(BaseParser):
    # Extra cost that we need to keep track when we do LLM calls
    llm_extra_calls_cost = 0

    # The model used to recover the format of the service report
    recover_with = 'gpt-4o-mini'

    # This is the output format that describes the output of service identification
    __OUTPUT_DESCRIPTION = str(
        Path(__file__).resolve().parent.parent / 'prompts/identifyService/identifyService.output.txt')

    def get_format_instructions(self) -> str:
        """
        Reads the format instructions from the output description file.
        """
        output_format = open(self.__OUTPUT_DESCRIPTION, 'r').read()
        return output_format

    def invoke(self, msg, *args, **kwargs) -> dict:
        """
        Entry point to parse the service identification output.
        """
        return self.parse(msg['output'])

    def fix_format(self, text: str) -> str:
        """
        Uses LLM to fix the format of the current service identification report.
        """
        fix_llm = LLMFunction.create(
            'Fix the format of the current service identification report according to the format instructions.\n\n# CURRENT SERVICE IDENTIFICATION REPORT\n{{ info.current_report }}\n\n# OUTPUT FORMAT\n{{ info.output_format }}',
            model=self.recover_with,
            use_logging=True,
            temperature=0.0,
            include_usage=True
        )
        fixed_text, usage = fix_llm(
            info=dict(
                current_report=text,
                output_format=self.get_format_instructions()
            )
        )

        self.llm_extra_calls_cost += usage.get_costs(self.recover_with)['total_cost']

        return fixed_text

    def extract_service_info(self, report: str) -> Dict:
        """
        Extracts the service identification information from the given report.
        """

        # Extract <protocol>
        protocol_match = re.search(r'<protocol>(.*?)</protocol>', report, re.DOTALL)
        if not protocol_match:
            raise Exception('Protocol not found in the report!')
        protocol = protocol_match.group(1).strip()

        # Extract <service_name>
        service_name_match = re.search(r'<service_name>(.*?)</service_name>', report, re.DOTALL)
        if not service_name_match:
            raise Exception('Service name not found in the report!')
        service_name = service_name_match.group(1).strip()

        # Extract <service_version>
        service_version_match = re.search(r'<service_version>(.*?)</service_version>', report, re.DOTALL)
        if not service_version_match:
            raise Exception('Service version not found in the report!')
        service_version = service_version_match.group(1).strip()


        # Extract <additional_information>
        additional_info_match = re.search(r'<additional_information>(.*?)</additional_information>', report, re.DOTALL)
        if not additional_info_match:
            raise Exception('Additional information not found in the report!')
        additional_info = additional_info_match.group(1).strip()

        # Combine extracted information
        service_report = {
            "protocol": protocol,
            "service_name": service_name,
            "service_version": service_version,
            "additional_information": additional_info
        }

        return service_report

    def parse(self, text: str) -> Dict:
        """
        Parses the service identification report, attempting to fix the format if necessary.
        """
        try_itr = 1
        while try_itr <= 3:
            m = re.search(r'<service_identification_report>([\s\S]*?)</service_identification_report>', text)
            if m:
                try:
                    service_info = self.extract_service_info(m.group(0))
                    print(f'✅ Regexp-Parser: Successfully parsed the service identification report from the output!')
                    return service_info
                except Exception as e:
                    print(f'🤡 Regexp-Error: Error parsing the service identification report - {e}')
                    print(
                        f'🤡 Regexp-Error: Trying to fix the format of the service identification report... Attempt {try_itr}!')
                    text = self.fix_format(text)
            else:
                print(f'🤡 Regexp-Error: Could not parse the service identification report from the output!')
                print(
                    f'🤡 Regexp-Error: Trying to fix the format of the service identification report... Attempt {try_itr}!')
                text = self.fix_format(text)
            try_itr += 1

        raise Exception('Failed to parse the service identification report after multiple attempts!')


class IdentifyServiceAgent(AgentWithHistory[dict, str]):
    __LLM_MODEL__ = 'gpt-4o-2024-08-06'
    current_file_path = Path(__file__).resolve()

    __SYSTEM_PROMPT_TEMPLATE__ = str(
        current_file_path.parent.parent / 'prompts/identifyService/identifyService.system.j2')
    __USER_PROMPT_TEMPLATE__ = str(current_file_path.parent.parent / 'prompts/identifyService/identifyService.user.j2')
    __OUTPUT_PARSER__ = ServiceReportParser
    __MAX_TOOL_ITERATIONS__ = 10
    __LLM_ARGS__ = {"temperature": 0.0}
    # Extra cost that we need to keep track when we do LLM calls
    extra_calls_cost = 0
    TARGET_IP: str
    TARGET_PORT: int
    TARGET_PROTOCOL: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.TARGET_IP = kwargs.get('TARGET_IP')
        self.TARGET_PORT = kwargs.get('TARGET_PORT')
        self.TARGET_PROTOCOL = kwargs.get('TARGET_PROTOCOL')

    def get_input_vars(self, *args, **kw):
        # Any returned dict will be use as an input to template the prompts
        # of this agent.
        vars = super().get_input_vars(*args, **kw)
        vars.update(
            TARGET_IP=self.TARGET_IP,
            TARGET_PORT=self.TARGET_PORT,
            TARGET_PROTOCOL=self.TARGET_PROTOCOL
        )
        return vars

    def get_cost(self, *args, **kw) -> float:
        total_cost = 0
        # We have to sum up all the costs of the LLM used by the agent
        for model_name, token_usage in self.token_usage.items():
            total_cost += token_usage.get_costs(model_name)['total_cost']
        # Taking into account the extra calls cost for recoveries from verification errors
        total_cost += self.extra_calls_cost
        return total_cost

    def get_available_tools(self):
        return TOOLS.values()
