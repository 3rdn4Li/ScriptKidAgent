class ServiceReport:
    def __init__(self, service_name: str,
                 service_version: str,
                 port: str,
                 additional_information: str,
                 ip: str,
                 protocol: str,
                 website_framework:str,
                 website_framework_version:str
                 ):
        """
        Initializes the ServiceReport object.

        Args:
            service_name (str): The name of the service.
            service_version (str): The version of the service.
            port (str): The port on which the service is running (as a string).
            additional_information (str): A string containing additional service information.
            ip (str): The IP address of the service.
            protocol (str): The protocol used by the service.
        """
        self.service_name = service_name
        self.service_version = service_version
        self.port = port
        self.additional_information = additional_information
        self.ip = ip
        self.protocol = protocol
        self.website_framework = website_framework
        self.website_framework_version = website_framework_version

    def __str__(self):
        """
        Converts the ServiceReport object to a formatted string in the specified XML format.

        Returns:
            str: The service identification report as a string.
        """
        report = f'<service_identification_report>\n'
        report += f'  <service_name>{self.service_name}</service_name>\n'
        report += f'  <service_version>{self.service_version}</service_version>\n'
        report += f'  <port>{self.port}</port>\n'
        report += f'  <ip>{self.ip}</ip>\n'
        report += f'  <protocol>{self.protocol}</protocol>\n'
        report += f'  <website_framework>{self.website_framework}</website_framework>\n'
        report += f'  <website_framework_version>{self.website_framework_version}</website_framework_version>\n'
        report += f'  <additional_information>\n    {self.additional_information}\n  </additional_information>\n'
        report += f'</service_identification_report>'
        return report

    def __hash__(self):
        """
        Returns a hash value for the object based on its string representation.

        Returns:
            int: The hash value of the object.
        """
        return hash(str(self))


class VulnReport:
    def __init__(self, service_report,
                 vulnerability_id: str,
                 capabilities: str,
                 vulnerability_description: str,
                 additional_information: str,
                 ):
        """
        Initializes the VulnReport object.
        
        Args:
            service_report (ServiceReport): The service report associated with the vulnerability.
            vulnerability_id (str): The ID of the vulnerability.
            vulnerability_description (str): A description of the vulnerability.
            additional_information (str): Additional information about the vulnerability.
        """
        self.service_report = service_report
        self.vulnerability_id = vulnerability_id
        self.capabilities = capabilities    
        self.vulnerability_description = vulnerability_description
        self.additional_information = additional_information

    def __str__(self):
        """
        Converts the VulnReport object to a formatted string in the specified XML format.
        
        Returns:
            str: The vulnerability identification report as a string.
        """
        report = f'<vulnerability_identification_report>\n'
        report += f'  <vulnerability_id>{self.vulnerability_id}</vulnerability_id>\n'
        report += f'  <vulnerability_description>{self.vulnerability_description}</vulnerability_description>\n'
        report += f'  <capabilities>{self.capabilities}</capabilities>\n'
        report += f'  <additional_information>\n    {self.additional_information}\n  </additional_information>\n'
        report += f'  {str(self.service_report)}\n'
        report += f'</vulnerability_identification_report>'
        return report

    def __hash__(self):
        """
        Returns a hash value for the object based on its string representation.
        
        Returns:
            int: The hash value of the object.
        """
        return hash(str(self))


class ExpReport:
    def __init__(self, service_report,
                 vulnerability_report,
                 is_success,
                 capabilities: str,
                 if_shell: str,
                 if_root: str,
                 message_history: list,
                 ):
        """
        Initializes the VulnReport object.

        Args:
            service_report (ServiceReport): The service report associated with the vulnerability.
            vulnerability_id (str): The ID of the vulnerability.
            vulnerability_description (str): A description of the vulnerability.
            additional_information (str): Additional information about the vulnerability.
        """
        self.service_report = service_report
        self.vulnerability_report = vulnerability_report
        self.is_success = is_success
        self.capabilities = capabilities
        self.if_shell = if_shell
        self.if_root = if_root
        self.message_history = message_history

    def __str__(self):
        """
        Converts the VulnReport object to a formatted string in the specified XML format.

        Returns:
            str: The vulnerability identification report as a string.
        """
        report = f'<exploitation_report>\n'
        report += f'  <exploitation_capabilities>{self.capabilities}</exploitation_capabilities>\n'
        report += f'  <exploitation_issuccess>{self.is_success}</exploitation_issuccess>\n'
        report += f'  <exploitation_ifshell>{self.if_shell}</exploitation_ifshell>\n'
        report += f'  <exploitation__ifroot>{self.if_root}</exploitation_ifroot>\n'
        report += f'  <exploitation_message_history>\n    {str(self.message_history)}\n  </exploitation_message_history>\n'
        report += f'  {str(self.service_report)}\n'
        report += f'  {str(self.vulnerability_report)}\n'
        report += f'</exploitation_report>'
        return report

    def __hash__(self):
        """
        Returns a hash value for the object based on its string representation.

        Returns:
            int: The hash value of the object.
        """
        return hash(str(self))
