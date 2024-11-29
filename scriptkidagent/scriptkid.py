import subprocess
import argparse
from typing import List, Dict
from scriptkidagent.stages.stage_infomation_gathering.common import scan_ip_segment
from scriptkidagent.stages.stage_infomation_gathering.agents.identify_service_agent import IdentifyServiceAgent
from scriptkidagent.stages.stage_vuln_identification.agents.identify_vuln_agent import IdentifyVulnAgent
from scriptkidagent.stages.stage_exploitation.exploit_agent import ExploitAgent
from scriptkidagent.models import ServiceReport, VulnReport

class ScriptKidAgent:
    def __init__(self, ip_segment: str):
        self.total_cost = 0
        self.ip_segment = None
        self.ip_to_service_reports = {}
        self.ip_to_vuln_reports = {}
        self.ip_to_protocol_to_ports = {}
        # ip to process object that is a shell
        self.ip_to_shell = {}
        
        # # for lateral movement
        # self.controlledip_to_new_targets = {}
        # self.ip_to_new_shell = {}

    def start(self, ip_segment: str):
        self.ip_to_protocol_to_ports = scan_ip_segment(ip_segment)
        print(self.ip_to_protocol_to_ports)
        for ip, protocols in self.ip_to_protocol_to_ports.items():
            for protocol, ports in protocols.items():
                for port in ports:
                    print(f"Identifying service on port {port} at {ip}, the protocol is {protocol}")
                    identify_service_agent = IdentifyServiceAgent(TARGET_IP=ip, TARGET_PORT=port, TARGET_PROTOCOL=protocol)
                    res = identify_service_agent.invoke()
                    service_report_raw = res.value
                    self.total_cost+=identify_service_agent.get_cost()

                    # convert this into a ServiceReport object
                    service_report=ServiceReport(
                        service_name=service_report_raw["service_name"],
                        service_version=service_report_raw["service_version"],
                        port=service_report_raw["port"],
                        additional_information=service_report_raw["additional_information"],
                        ip=service_report_raw["ip"],
                        protocol=service_report_raw["protocol"]
                    )
                    if ip not in self.ip_to_service_reports:
                        self.ip_to_service_reports[ip] = dict()
                    self.ip_to_service_reports[ip][port] = service_report
        
        for ip, port in self.ip_to_service_reports.items():
            breakpoint()
            identify_vuln_agent = IdentifyVulnAgent(ip, self.ip_to_service_reports[ip][port])
            pass
            # produce VulnReport
        
        for ip, vuln_report in self.ip_to_vuln_reports.items():
            exploit_agent = ExploitAgent(ip, vuln_report.service_report.port, vuln_report)
            pass
        
        # # for lateral movement
        # while self.ip_to_new_shell:
            
        #     for ip, shell in self.ip_to_new_shell.items():
        #         # let agent perform scanning using nmap, if no nmap, install nmap
        #         # check whether the returned ip and port is in the ip_to_protocol_to_ports
        #         # if not, add it to the controlledip_to_new_targets
        #         pass
            
        #     for ip, new_targets in self.controlledip_to_new_targets.items():
        #         # let agent perform information gathering, vuln identification, and exploitation on the new targets
        #         pass
            

def main():
    """
    Entry point for the ScriptKidAgent command-line tool.
    """
    parser = argparse.ArgumentParser(description='ScriptKidAgent')
    parser.add_argument('--ip_segment', type=str, help='IP segment to exploit (e.g., 192.168.1.0/24)')
    args = parser.parse_args()

    scriptkid = ScriptKidAgent(args.ip_segment)
    scriptkid.start(args.ip_segment)


if __name__ == '__main__':
    main()