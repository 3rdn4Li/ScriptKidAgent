import re
from agentlib import AgentWithHistory, LLMFunction
from pathlib import Path
from typing import Dict, List
from scriptkidagent.tools.tools import execute_in_bash, execute_cmds_in_msfconsole
from agentlib.lib.common.parsers import BaseParser
from scriptkidagent.models import ServiceReport

TOOLS = {"execute_in_bash": execute_in_bash, "execute_cmds_in_msfconsole": execute_cmds_in_msfconsole}

class VulnReportParser(BaseParser):
    # Extra cost that we need to keep track when we do LLM calls
    llm_extra_calls_cost = 0

    # The model used to recover the format of the vulnerability report
    recover_with = 'gpt-4o-mini'

    # This is the output format that describes the output of vulnerability identification
    __OUTPUT_DESCRIPTION = str(
        Path(__file__).resolve().parent.parent / 'prompts/identifyVuln/identifyVuln.output.txt')

    def get_format_instructions(self) -> str:
        """
        Reads the format instructions from the output description file.
        """
        with open(self.__OUTPUT_DESCRIPTION, 'r') as f:
            output_format = f.read()
        return output_format

    def invoke(self, msg, *args, **kwargs) -> dict:
        """
        Entry point to parse the vulnerability identification output.
        """
        return self.parse(msg['output'])

    def fix_format(self, text: str) -> str:
        """
        Uses LLM to fix the format of the current vulnerability identification report.
        """
        fix_llm = LLMFunction.create(
            'Fix the format of the current vulnerability identification report according to the format instructions.\n\n# CURRENT VULNERABILITY IDENTIFICATION REPORT\n{{ info.current_report }}\n\n# OUTPUT FORMAT\n{{ info.output_format }}',
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

    def extract_vulnerability_info(self, report: str) -> Dict:
        """
        Extracts the vulnerability identification information from a single vulnerability report.
        """
        # Extract <vulnerability_id>
        vuln_id_match = re.search(r'<vulnerability_id>(.*?)</vulnerability_id>', report, re.DOTALL)
        if not vuln_id_match:
            raise Exception('Vulnerability ID not found in the report!')
        vulnerability_id = vuln_id_match.group(1).strip()

        # Extract <vulnerability_description>
        vuln_desc_match = re.search(r'<vulnerability_description>(.*?)</vulnerability_description>', report, re.DOTALL)
        if not vuln_desc_match:
            raise Exception('Vulnerability description not found in the report!')
        vulnerability_description = vuln_desc_match.group(1).strip()

        # Extract <capabilities>
        capabilities_match = re.search(r'<capabilities>(.*?)</capabilities>', report, re.DOTALL)
        if not capabilities_match:
            raise Exception('Capabilities not found in the report!')
        capabilities_content = capabilities_match.group(1).strip()
        capabilities = re.findall(r'<capability>(.*?)</capability>', capabilities_content, re.DOTALL)
        capabilities = [cap.strip() for cap in capabilities]

        # Extract <additional_information>
        additional_info_match = re.search(r'<additional_information>(.*?)</additional_information>', report, re.DOTALL)
        if not additional_info_match:
            raise Exception('Additional information not found in the report!')
        additional_information = additional_info_match.group(1).strip()

        # Combine extracted information
        vulnerability_report = {
            "vulnerability_id": vulnerability_id,
            "vulnerability_description": vulnerability_description,
            "capabilities": capabilities,
            "additional_information": additional_information
        }

        return vulnerability_report

    def parse(self, text: str) -> List[Dict]:
        """
        Parses the vulnerability identification reports, attempting to fix the format if necessary.
        Returns a list of vulnerability reports.
        """
        try_itr = 1
        while try_itr <= 3:
            m = re.search(r'<vulnerability_identification_reports>([\s\S]*?)</vulnerability_identification_reports>', text)
            if m:
                reports_content = m.group(1)
                report_matches = re.findall(r'<vulnerability_identification_report>([\s\S]*?)</vulnerability_identification_report>', reports_content)
                if report_matches:
                    vulnerability_reports = []
                    for report_text in report_matches:
                        try:
                            vulnerability_info = self.extract_vulnerability_info(report_text)
                            vulnerability_reports.append(vulnerability_info)
                        except Exception as e:
                            print(f'🤡 Regexp-Error: Error parsing one of the vulnerability reports - {e}')
                            print(f'🤡 Regexp-Error: Trying to fix the format of the vulnerability identification report... Attempt {try_itr}!')
                            text = self.fix_format(text)
                            break  # Exit the loop to retry parsing after format fixing
                    else:
                        print('✅ Regexp-Parser: Successfully parsed all vulnerability identification reports from the output!')
                        return vulnerability_reports
                else:
                    print(f'🤡 Regexp-Error: No <vulnerability_identification_report> entries found!')
                    print(f'🤡 Regexp-Error: Trying to fix the format... Attempt {try_itr}!')
                    text = self.fix_format(text)
            else:
                print(f'🤡 Regexp-Error: Could not find <vulnerability_identification_reports> in the output!')
                print(f'🤡 Regexp-Error: Trying to fix the format... Attempt {try_itr}!')
                text = self.fix_format(text)
            try_itr += 1

        raise Exception('Failed to parse the vulnerability identification reports after multiple attempts!')



class IdentifyVulnAgent(AgentWithHistory[dict, str]):
    __LLM_MODEL__ = 'gpt-4o-2024-08-06'
    current_file_path = Path(__file__).resolve()

    __SYSTEM_PROMPT_TEMPLATE__ = str(
        current_file_path.parent.parent / 'prompts/identifyVuln/identifyVuln.system.j2')
    __USER_PROMPT_TEMPLATE__ = str(current_file_path.parent.parent / 'prompts/identifyVuln/identifyVuln.user.j2')
    __OUTPUT_PARSER__ = VulnReportParser
    __MAX_TOOL_ITERATIONS__ = 10
    __LLM_ARGS__ = {"temperature": 0.0}
    # Extra cost that we need to keep track when we do LLM calls
    extra_calls_cost = 0
    SERVICE_REPORT_STR: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.SERVICE_REPORT_STR = kwargs.get('SERVICE_REPORT_STR')

    def get_input_vars(self, *args, **kw):
        # Any returned dict will be use as an input to template the prompts
        # of this agent.
        vars = super().get_input_vars(*args, **kw)
        vars.update(
            SERVICE_REPORT_STR=self.SERVICE_REPORT_STR
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
