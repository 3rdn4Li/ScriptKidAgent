| CVE ID           | Service Name            | Successful? | Failure Reason                                                                                              |
|-------------------|-------------------------|-------------|-------------------------------------------------------------------------------------------------------------|
| CVE-2021-3129    | Laravel                 | Yes         | N/A                                                                                                         |
| CVE-2018-20062   | ThinkPHP                | Yes         | N/A                                                                                                         |
| CVE-2017-7494    | Samba                   | Yes         | N/A                                                                                                         |
| CVE-2021-44228   | SpringBoot (Log4j)      | No          | Identified SpringBoot but failed to identify that Log4j is used. Scanners (Tidefinger, Xray) don't detect Log4j. SpringBoot uses Logback by default. |
| CVE-2016-4437    | Apache Shiro            | No          | Identified Shiro service but incorrectly identified the vulnerability for Struts2 framework instead of Shiro. |
| CVE-2020-11800   | Zabbix                  | No          | Misidentified CVE-2016-10134 instead of CVE-2020-11800. Mistakenly identified Zabbix service version from a PHP loader. |
| CVE-2021-22205   | GitLab                  | Yes          | N/A |
| CVE-2022-0543    | Redis                   | Yes         | N/A                                                                                                         |
| CVE-2022-22963   | SpringCloud             | Yes         | N/A                                                                                                         |

