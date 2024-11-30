class ServiceReport:
    def __init__(self, service_name: str,
                 service_version: str,
                 port: str,
                 additional_information: str,
                 ip: str,
                 protocol: str):
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
