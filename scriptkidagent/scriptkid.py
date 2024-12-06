import subprocess
import argparse
import os
from typing import List, Dict
from scriptkidagent.stages.stage_infomation_gathering.common import scan_ip_segment
from scriptkidagent.stages.stage_infomation_gathering.agents.identify_service_agent import IdentifyServiceAgent
from scriptkidagent.stages.stage_vuln_identification.agents.identify_vuln_agent import IdentifyVulnAgent
from scriptkidagent.stages.stage_exploitation.exploit_agent import ExploitAgent
from scriptkidagent.models import ServiceReport, VulnReport, ExpReport


class ScriptKidAgent:
    def __init__(self, ip_segment: str, lhost_ip: str, srvhost_ip: str):
        self.total_cost = 0
        self.ip_segment = ip_segment
        self.lhost_ip = lhost_ip
        self.srvhost_ip = srvhost_ip
        self.ip_to_port_to_service_reports = {}
        self.ip_to_port_to_vuln_reports = {}
        self.ip_to_port_to_exploit_reports = {}
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
                    print(f"####################### Identifying service on port {port} at {ip}, the protocol is {protocol} #######################")
                    identify_service_agent = IdentifyServiceAgent(TARGET_IP=ip, TARGET_PORT=port,
                                                                  TARGET_PROTOCOL=protocol)
                    res = identify_service_agent.invoke()
                    service_report_raw = res.value
                    self.total_cost += identify_service_agent.get_cost()

                    # convert this into a ServiceReport object
                    if service_report_raw and service_report_raw["service_name"].lower() != "unknown" and service_report_raw["service_version"].lower() != "unknown" or service_report_raw["website_framework"].lower() != "unknown":
                        service_report = ServiceReport(
                            service_name=service_report_raw["service_name"],
                            service_version=service_report_raw["service_version"],
                            port=str(port),
                            website_framework=service_report_raw["website_framework"],
                            website_framework_version=service_report_raw["website_framework_version"],
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
                print(f"####################### Identifying Vuln on port {port} at {ip} #######################")
                print(f'The service name is {service_report.service_name}')
                identify_vuln_agent = IdentifyVulnAgent(SERVICE_REPORT_STR=str(service_report))
                res = identify_vuln_agent.invoke()
                vuln_report_raws = res.value
                self.total_cost += identify_vuln_agent.get_cost()
                for vuln_report_raw in vuln_report_raws:                
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
                        if port not in self.ip_to_port_to_vuln_reports[ip]:
                            self.ip_to_port_to_vuln_reports[ip][port] = []
                        self.ip_to_port_to_vuln_reports[ip][port].append(vuln_report)
        
        # Save the vuln reports to a file
        if os.path.exists("vuln_reports.txt"):
            os.remove("vuln_reports.txt")
        with open("vuln_reports.txt", "w+") as f:
            for ip, port_to_vuln_report in self.ip_to_port_to_vuln_reports.items():
                for port, vuln_reports in port_to_vuln_report.items():
                    f.write(f"################## {ip}:{port} ##################\n")
                    for vuln_report in vuln_reports:
                        f.write(f"{vuln_report}\n\n")
                    f.write(f"################## END {ip}:{port} ##################\n")

        for ip, port_to_vuln_reports in self.ip_to_port_to_vuln_reports.items():
            for port, vuln_reports in port_to_vuln_reports.items():
                for vuln_report in vuln_reports:
                    print(f"################## Exploiting vulnerability {vuln_report.vulnerability_id} on port {port} at {ip} ##################")
                    print(f'The vulnerability id is {vuln_report.vulnerability_id}')
                    exploit_agent = ExploitAgent(ip, self.lhost_ip, self.srvhost_ip, vuln_report.service_report.port, vuln_report)
                    exp_success, exp_temp_report, process = exploit_agent.exploit()

                    exp_report = ExpReport(
                        service_report=self.ip_to_port_to_service_reports[ip][port],
                        vulnerability_report=self.ip_to_port_to_vuln_reports[ip][port],
                        is_success=exp_success,
                        capabilities=exp_temp_report["capabilities"],
                        if_shell=exp_temp_report["if_shell"],
                        if_root=exp_temp_report["if_root"],
                        message_history=exp_temp_report["message_history"]
                    )
                    if ip not in self.ip_to_port_to_exploit_reports:
                        self.ip_to_port_to_exploit_reports[ip] = dict()
                    self.ip_to_port_to_exploit_reports[ip][port] = exp_report

        if os.path.exists("exp_reports.txt"):
            os.remove("exp_reports.txt")
        with open("exp_reports.txt", "w+") as f:
            for ip, port_to_expn_report in self.ip_to_port_to_exploit_reports.items():
                for port, exp_report in port_to_expn_report.items():
                    f.write(f"{ip}:{port}\n")
                    f.write(f"{exp_report}\n\n")

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
    parser.add_argument('--lhost_ip', type=str, help='lhost IP address', required=False, default='You should figure out the lhost IP address')
    parser.add_argument('--srvhost_ip', type=str, help='srvhost for metasploit', required=False, default='You should figure out the srvhost IP address')
    args = parser.parse_args()

    scriptkid = ScriptKidAgent(args.ip_segment, args.lhost_ip, args.srvhost_ip) 
    scriptkid.start()


if __name__ == '__main__':
    main()
