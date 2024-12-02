import subprocess
import argparse
import os
from typing import List, Dict
from scriptkidagent.stages.stage_infomation_gathering.common import scan_ip_segment
from scriptkidagent.stages.stage_infomation_gathering.agents.identify_service_agent import IdentifyServiceAgent
from scriptkidagent.stages.stage_vuln_identification.agents.identify_vuln_agent import IdentifyVulnAgent
from scriptkidagent.stages.stage_exploitation.exploit_agent import ExploitAgent
from scriptkidagent.models import ServiceReport, VulnReport


class ScriptKidAgent:
    def __init__(self, ip_segment: str):
        self.total_cost = 0
        self.ip_segment = ip_segment
        self.ip_to_port_to_service_reports = {}
        self.ip_to_port_to_vuln_reports = {}
        self.ip_to_protocol_to_ports = {}
        # ip to process object that is a shell
        self.ip_to_shell = {}

        # # for lateral movement
        # self.controlledip_to_new_targets = {}
        # self.ip_to_new_shell = {}

    def start(self):
        self.ip_to_protocol_to_ports = scan_ip_segment(self.ip_segment)
        print(self.ip_to_protocol_to_ports)
        for ip, protocols in self.ip_to_protocol_to_ports.items():
            for protocol, ports in protocols.items():
                for port in ports:
                    print(f"Identifying service on port {port} at {ip}, the protocol is {protocol}")
                    identify_service_agent = IdentifyServiceAgent(TARGET_IP=ip, TARGET_PORT=port,
                                                                  TARGET_PROTOCOL=protocol)
                    res = identify_service_agent.invoke()
                    service_report_raw = res.value
                    self.total_cost += identify_service_agent.get_cost()

                    # convert this into a ServiceReport object
                    if service_report_raw and service_report_raw["service_name"].lower() != "unknown" and service_report_raw["service_version"].lower() != "unknown":
                        service_report = ServiceReport(
                            service_name=service_report_raw["service_name"],
                            service_version=service_report_raw["service_version"],
                            port=str(port),
                            additional_information=service_report_raw["additional_information"],
                            ip=str(ip),
                            protocol=service_report_raw["protocol"]
                        )
                        if ip not in self.ip_to_port_to_service_reports:
                            self.ip_to_port_to_service_reports[ip] = dict()
                        self.ip_to_port_to_service_reports[ip][port] = service_report
        
        # Save the service reports to a file
        if os.path.exists("service_reports.txt"):
            os.remove("service_reports.txt")
        with open("service_reports.txt", "w+") as f:
            for ip, port_to_service_report in self.ip_to_port_to_service_reports.items():
                for port, service_report in port_to_service_report.items():
                    f.write(f"{ip}:{port}\n")
                    f.write(f"{service_report}\n\n")

        for ip, port_to_service_report in self.ip_to_port_to_service_reports.items():
            for port, service_report in port_to_service_report.items():
                identify_vuln_agent = IdentifyVulnAgent(SERVICE_REPORT_STR=str(service_report))
                res = identify_vuln_agent.invoke()
                vuln_report_raw = res.value
                self.total_cost += identify_vuln_agent.get_cost()
                
                if vuln_report_raw and vuln_report_raw["vulnerability_id"].lower() != "unknown":
                    vuln_report = VulnReport(
                        service_report=self.ip_to_port_to_service_reports[ip][port],
                        vulnerability_id=vuln_report_raw["vulnerability_id"],
                        capabilities=vuln_report_raw["capabilities"],
                        vulnerability_description=vuln_report_raw["vulnerability_description"],
                        additional_information=vuln_report_raw["additional_information"]
                    )
                    if ip not in self.ip_to_port_to_vuln_reports:
                        self.ip_to_port_to_vuln_reports[ip] = dict()
                    self.ip_to_port_to_vuln_reports[ip][port] = vuln_report
        
        # Save the vuln reports to a file
        if os.path.exists("vuln_reports.txt"):
            os.remove("vuln_reports.txt")
        with open("vuln_reports.txt", "w+") as f:
            for ip, port_to_vuln_report in self.ip_to_port_to_vuln_reports.items():
                for port, vuln_report in port_to_vuln_report.items():
                    f.write(f"{ip}:{port}\n")
                    f.write(f"{vuln_report}\n\n")

        for ip, port_to_vuln_report in self.ip_to_port_to_vuln_reports.items():
            for port, vuln_report in port_to_vuln_report.items():
                exploit_agent = ExploitAgent(ip, vuln_report.service_report.port, vuln_report)
                exploit_agent.exploit()

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
    parser.add_argument('--ip_segment', type=str, help='IP segment to exploit (e.g., 192.168.1.0/24) or single IP address, for test, you can use 127.0.0.1')
    args = parser.parse_args()

    scriptkid = ScriptKidAgent(args.ip_segment)
    scriptkid.start()


if __name__ == '__main__':
    main()
