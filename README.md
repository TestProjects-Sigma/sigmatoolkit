# SigmaToolkit

**Version: 1.6.0**

Sigma's IT Swiss Army Knife - A comprehensive PyQt5-based GUI application designed for system and network administrators to perform various IT troubleshooting tasks efficiently. Your all-in-one toolkit for daily IT operations, infrastructure monitoring, and security compliance.

## 🚀 Features

### 🔐 AD Password Checker (v1.6.0) ✨ **NEW**
- **Comprehensive Password Monitoring**: Real-time Active Directory password expiration tracking with exact day counts
- **Security Compliance**: Monitor password policies, track expired accounts, and ensure security standards
- **Visual Status Indicators**: Color-coded displays with 🔴 Expired, 🟡 Expiring Soon, ✅ Active status
- **Secure LDAP Connection**: LDAPS with SSL/TLS encryption, NTLM authentication, and certificate validation
- **Advanced User Management**: Track disabled accounts, never-expiring passwords, and comprehensive user information
- **Auto-Refresh Monitoring**: Continuous monitoring with configurable intervals for proactive management
- **Comprehensive Reporting**: Export detailed CSV reports, summary dashboards, and compliance documentation
- **Configuration Management**: Save/load AD connection settings with secure credential handling
- **Multi-Tab Interface**: Organized views for user lists, summary reports, and configuration management
- **Enterprise Security**: No password storage, minimal service account permissions, and audit-ready logging

### 🟢 Service Monitor (v1.5.0)
- **Real-time Service Monitoring**: Monitor Microsoft 365, cloud providers, and custom services with live status updates
- **Auto-refresh Capability**: Continuous monitoring with configurable 30-second intervals
- **Multiple Check Types**: HTTP/HTTPS status, Ping connectivity, Port availability, DNS resolution, and Custom API endpoints
- **Pre-configured Service Categories**: One-click addition of Microsoft 365, Infrastructure (DNS), and Cloud Provider services
- **Custom Service Management**: Add any HTTP endpoint, server, or service with flexible configuration options
- **Persistent Configuration**: Auto-save/load functionality ensures your services are remembered between sessions
- **Status Summary Dashboard**: Real-time overview with 🟢 Healthy, 🟡 Warning, 🔴 Critical indicators
- **Configuration Management**: Save/load service configurations for backup, sharing, and team collaboration
- **Response Time Tracking**: Monitor service performance with millisecond precision
- **Export Capabilities**: Generate status reports for documentation and incident management

### 🌐 Network Testing (v1.0.0)
- **Ping Test**: Test connectivity to hosts with customizable packet count
- **Traceroute**: Trace network path to destination hosts
- **Port Scanner**: Scan single ports, port ranges, or comma-separated port lists
- **DNS Lookup**: Basic forward and reverse DNS lookups
- **Quick Actions**: One-click tests for common DNS servers and default gateway
- **System Network Information**: Auto-detection of local IP, gateway, DNS servers, and network interfaces

### 🔍 DNS Testing (v1.1.0)
- **Forward/Reverse Lookup**: Domain ↔ IP address resolution
- **MX Records**: Mail server configuration analysis
- **TXT Records**: SPF, DKIM, and other text records for email authentication
- **NS Records**: Name server information and delegation
- **CNAME Records**: Domain aliases and canonical names
- **AAAA Records**: IPv6 address resolution
- **A Records**: IPv4 address resolution with detailed analysis
- **DNS Server Selection**: Test with Google, Cloudflare, Quad9, or custom DNS servers
- **Comprehensive Analysis**: All-in-one DNS record lookup with intelligent parsing

### 📧 SMTP Testing (v1.2.0)
- **Connection Testing**: Verify SMTP server connectivity and capabilities
- **Optional Authentication**: Test with credentials OR without for relay testing
- **Relay Testing**: Test internal mail servers without authentication requirements
- **Email Sending**: Send actual test emails with delivery confirmation
- **Encryption Support**: TLS (STARTTLS) and SSL connection options
- **Port Scanning**: Test connectivity to common SMTP ports (25, 465, 587, 2525)
- **MX Record Integration**: Check domain mail server configuration
- **Quick Presets**: Pre-configured settings for Gmail, Outlook, Office 365, Yahoo
- **Comprehensive Testing**: All-in-one SMTP server analysis and troubleshooting
- **Flexible Authentication**: Supports both authenticated and open relay configurations

### ⚡ Speed Testing (v1.3.0)
- **Official Speedtest.net Integration**: Uses genuine speedtest.net CLI for maximum accuracy
- **Professional Speed Analysis**: LCD-style displays with real-time progress tracking
- **Comprehensive Testing Options**: Multiple test methods and server selection
- **Advanced Features**: Multi-CLI support with intelligent server selection
- **For Gigabit Connections**: Accurately measures 500+ Mbps connections
- **LAN Speed Testing**: Local network performance analysis
- **Network Device Detection**: Auto-discovery of local devices
- **Real-time Monitoring**: Live download/upload speed and latency displays

### 📨 Mail Header Analysis (v1.4.0)
- **Comprehensive Header Analysis**: Parse and analyze email headers with detailed insights
- **Email Authentication Verification**: Complete SPF, DKIM, and DMARC validation
- **Delivery Path Tracking**: Trace email route with timestamps and delay analysis
- **Spam Detection**: IP reputation checking and suspicious pattern identification
- **Interactive Analysis**: Multiple tabs for different analysis types
- **Security Assessment**: Identify potential spoofing and phishing indicators
- **Export Capabilities**: Save analysis results for documentation and reports
- **Sample Headers**: Built-in examples for testing and learning
- **File Upload Support**: Load .eml files directly for analysis

#### 📧 Mail Analysis Features Detail:
- **📧 Header Analysis Tab**:
  - Parse email headers from raw text or .eml files
  - Identify sender, recipient, subject, and routing information
  - Detect suspicious patterns and missing security headers
  - Generate comprehensive analysis reports with recommendations

- **🔐 Email Authentication Tab**:
  - SPF Record Analysis: Validate sender IP against DNS policies
  - DKIM Signature Verification: Check cryptographic signatures and key strength
  - DMARC Policy Assessment: Analyze domain policies and alignment settings
  - Comprehensive Authentication Reports: Combined analysis with security recommendations

- **🛤️ Delivery Path Tab**:
  - Email Route Visualization: Track message path through mail servers
  - Timestamp Analysis: Calculate delivery delays and identify bottlenecks
  - Server Identification: Extract and analyze intermediate mail servers
  - Loop Detection: Identify potential mail routing loops

- **🛡️ Spam Analysis Tab**:
  - IP Reputation Checking: Verify sender IP against reputation databases
  - Blacklist Verification: Check against common spam blacklists
  - Content Pattern Analysis: Identify suspicious content indicators
  - Risk Assessment: Generate overall spam probability scores

### 🔌 Port Listener (v1.5.1) - Optional
- **Firewall Testing**: Test port accessibility and firewall rules
- **Connection Monitoring**: Monitor incoming connections with real-time logging
- **Multiple Response Types**: HTTP OK, Echo, or Silent response modes
- **Real-time Statistics**: Connection counting, uptime tracking, and client monitoring
- **Network Validation**: Verify connectivity through corporate firewalls and load balancers

### 🛠️ General Features
- **Multi-Tab Interface**: Organized testing categories with clean navigation and prioritized security tools
- **Debug Mode**: Toggle detailed logging for advanced troubleshooting
- **Real-time Output**: Live results with timestamp and color-coded log levels
- **Copy Results**: One-click copying of output to clipboard
- **Professional UI**: Modern interface designed for efficiency, security compliance, and infrastructure monitoring
- **Cross-Platform**: Works seamlessly on Windows, Linux, and macOS
- **Export Functionality**: Save analysis results, service reports, AD compliance reports, and configuration backups
- **Persistent Storage**: Auto-save configurations and settings

## 📋 Requirements

- **Python 3.7+**
- **Windows environment** (for Active Directory access - AD Password Checker)
- **Network access** to your infrastructure (Active Directory, monitored services)
- **Service accounts** with appropriate permissions for AD and monitored services

## 🛠️ Installation

### 1. Clone or Download
```bash
git clone <repository-url>
cd sigmatoolkit
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

## ⚙️ Configuration

### AD Password Checker Configuration

Fill in the AD Password Checker tab with your Active Directory details:

| Field | Example | Description |
|-------|---------|-------------|
| **Server** | `dc01.company.com` | Your AD domain controller FQDN |
| **Port** | `636` (SSL) or `389` | LDAP port (636 recommended for security) |
| **Use SSL/TLS** | ✅ Checked | Enable secure connection (recommended) |
| **Domain** | `COMPANY` | Your Windows domain name (short format) |
| **Base DN** | `DC=company,DC=com` | LDAP search base for users |
| **Username** | `serviceaccount` | AD account with read permissions |
| **Password** | `your_password` | Account password (not saved to config) |

### Service Monitor Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| **Auto Refresh** | Disabled | Automatically refresh service status |
| **Refresh Interval** | 30 seconds | How often to refresh service status |
| **Pre-configured Services** | Available | Microsoft 365, Google Workspace, AWS, Azure |

### Application Settings

| Setting | Default | Description |
|---------|---------|-------------|
| **Debug Mode** | Disabled | Enable detailed logging for troubleshooting |
| **Auto-save** | Enabled | Automatically save configurations |
| **Export Format** | CSV/TXT | Default export format for reports |

## 🎯 Usage

### 1. AD Password Monitoring
1. **Configure Connection**: Fill in AD connection settings in the AD Password Checker tab
2. **Test Connection**: Click "Test Connection" to verify settings
3. **Save Configuration**: Click "Save Configuration" to store settings (passwords not saved)
4. **Refresh Data**: Click "Refresh Data" to load user password information
5. **Monitor Status**: Review results with color-coded expiry indicators
6. **Export Reports**: Generate CSV reports for compliance documentation
7. **Auto-Refresh**: Enable automatic monitoring for continuous compliance

### 2. Service Infrastructure Monitoring
1. **Add Services**: Use pre-configured categories or add custom services
2. **Configure Monitoring**: Set check types (HTTP, Ping, Port, DNS)
3. **Start Monitoring**: Enable auto-refresh for continuous monitoring
4. **Review Status**: Monitor 🟢 Healthy, 🟡 Warning, 🔴 Critical indicators
5. **Export Reports**: Generate status reports for incident documentation

### 3. Network and Security Testing
1. **Network Testing**: Use ping, traceroute, and port scanning for connectivity
2. **DNS Analysis**: Comprehensive DNS record analysis and troubleshooting
3. **SMTP Testing**: Email server connectivity and authentication testing
4. **Speed Testing**: Internet and LAN performance analysis
5. **Mail Analysis**: Email header analysis for security and deliverability

## 📊 Understanding AD Password Results

### Password Status Indicators

| Display | Meaning | Color | Action Required |
|---------|---------|-------|-----------------|
| `15` | Password expires in 15 days | Normal | Monitor |
| `3` | Password expires in 3 days | 🟡 Yellow | Notify User |
| `-5` | Password expired 5 days ago | 🔴 Red | **Immediate Action** |
| `Never` | Password never expires | Normal | Review Policy |
| `Disabled` | Account is disabled | Normal | Cleanup Review |

### Compliance Reporting

- **Total Users**: Complete user count in monitored OUs
- **Expired Passwords**: Users requiring immediate password reset
- **Expiring Soon**: Users needing proactive notification
- **Policy Exceptions**: Accounts with non-standard settings
- **Security Risks**: Accounts requiring security review

## 🔧 Integration Capabilities

### AD Password API Integration

```python
from ad.ad_tools import ADPasswordTools

# Initialize the AD tools
ad_tools = ADPasswordTools(logger)

# Get password data programmatically
params = {
    "server": "dc.company.com",
    "port": 636,
    "use_ssl": True,
    "domain": "COMPANY",
    "username": "serviceaccount",
    "password": "password",
    "base_dn": "DC=company,DC=com"
}

# Test connection
success_callback = lambda msg: print(f"Success: {msg}")
error_callback = lambda err: print(f"Error: {err}")
worker = ad_tools.test_connection_async(params, success_callback, error_callback)
```

### Service Monitor API Integration

```python
from services.services_tools import ServiceMonitorTools

# Initialize service monitoring
service_tools = ServiceMonitorTools(logger)

# Add Microsoft 365 services
service_tools.add_microsoft365_services()

# Monitor custom service
service_tools.add_service("Custom API", "https://api.company.com/health", "HTTP")

# Get status summary
summary = service_tools.get_status_summary()
print(f"Healthy: {summary['healthy']}, Critical: {summary['critical']}")
```

## 🛡️ Security Best Practices

### Active Directory Security
- **Use dedicated service accounts** with minimal required permissions
- **Always use SSL/TLS** (port 636) in production environments
- **Monitor password compliance** daily for security posture
- **Regular security audits** of accounts that never expire
- **Secure credential handling** - passwords never stored in config files

### Service Account Permissions
The AD service account needs:
- **Read access** to user objects in Active Directory
- **Permission to query** user attributes: `sAMAccountName`, `displayName`, `mail`, `pwdLastSet`, `userAccountControl`
- **No elevated privileges** required
- **Regular password rotation** following security policies

### Infrastructure Monitoring Security
- **Secure API endpoints** for service monitoring
- **Network access controls** for monitoring traffic
- **Audit logging** for all monitoring activities
- **Credential management** for service authentication

### Network Security
- **Firewall rules** allowing LDAP/LDAPS traffic to domain controllers
- **VPN or secure network** when accessing from remote locations
- **Monitor connections** in LDAP server logs for security events
- **Regular security assessments** of monitoring infrastructure

## 🔍 Troubleshooting

### AD Password Checker Issues

#### "Connection Error: unsupported hash type MD4"
- **Solution**: Install `pycryptodome`: `pip install pycryptodome==3.19.0`
- **Cause**: Newer Python versions disable MD4 needed for NTLM authentication

#### "LDAP3 library not available"
- **Solution**: Install required dependencies: `pip install ldap3==2.9.1`
- **Verification**: Test import in Python: `import ldap3`

#### "Test connection failed"
- **Check server name**: Try both short name (DC01) and FQDN (dc01.company.com)
- **Verify port**: 636 for SSL, 389 for non-SSL
- **Check credentials**: Ensure username/password are correct
- **Network access**: Verify firewall allows LDAP connections
- **Service account**: Ensure account is not locked or disabled

#### "No results returned"
- **Verify Base DN**: Should match your domain structure (DC=company,DC=com)
- **Check permissions**: Service account needs read access to user objects
- **Review search scope**: Ensure users exist in the specified organizational unit
- **LDAP query**: Test with tools like LDP.exe to verify query syntax

#### "Authentication failed"
- **Try different formats**: Application tries multiple formats automatically
- **Domain format**: Use short domain name (COMPANY) not FQDN (company.com)
- **Account status**: Ensure service account is not locked, disabled, or expired
- **Password policy**: Verify service account password meets complexity requirements

### Service Monitor Issues

#### "Service not responding"
- **Check URL format**: Ensure proper HTTP/HTTPS protocol specification
- **Network connectivity**: Verify network access to monitored services
- **Firewall rules**: Ensure monitoring traffic is allowed
- **Service status**: Check if the actual service is running

#### "SSL/TLS errors"
- **Certificate validation**: Check SSL certificate validity
- **Protocol versions**: Ensure compatible TLS versions
- **Certificate trust**: Verify certificate chain trust

### General Troubleshooting

#### Debug Mode
Enable debug output in the application:
1. **Click "Toggle Debug"** in the main interface
2. **Review detailed logs** in the output panel
3. **Export logs** for further analysis

#### Performance Issues
- **Reduce refresh intervals** for better performance
- **Limit concurrent monitoring** to prevent resource exhaustion
- **Monitor system resources** during large-scale operations

#### Getting Help
1. **Check console output** for detailed error messages
2. **Verify configuration** with test functions first
3. **Review security logs** for authentication and authorization issues
4. **Test with minimal configuration** before complex setups

## 📁 File Structure

```
sigmatoolkit/
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                  # This documentation
├── config/
│   └── settings.py            # Application settings management
├── core/
│   ├── __init__.py
│   ├── base_tab.py           # Base class for tabs
│   └── logger.py             # Logging functionality
├── ad/                       # AD Password Checker module
│   ├── __init__.py
│   ├── ad_tab.py            # AD Password Checker tab
│   └── ad_tools.py          # AD operations and tools
├── services/                 # Service Monitor module
│   ├── __init__.py
│   ├── services_tab.py      # Service monitoring tab
│   └── services_tools.py    # Service monitoring tools
├── network/
│   ├── __init__.py
│   ├── network_tab.py       # Network testing tab
│   └── network_tools.py     # Network utilities
├── dns/
│   ├── __init__.py
│   ├── dns_tab.py          # DNS testing tab
│   └── dns_tools.py        # DNS utilities
├── smtp/
│   ├── __init__.py
│   ├── smtp_tab.py         # SMTP testing tab
│   └── smtp_tools.py       # SMTP utilities
├── speedtest/
│   ├── __init__.py
│   ├── speedtest_tab.py    # Speed testing tab
│   └── speedtest_tools.py  # Speed testing utilities
├── mail/                    # Mail analysis module (optional)
│   ├── __init__.py
│   ├── mail_tab.py         # Mail header analysis tab
│   └── mail_tools.py       # Mail analysis tools
├── portlistener/           # Port listener module (optional)
│   ├── __init__.py
│   ├── port_listener_tab.py # Port listener tab
│   └── port_listener_tools.py # Port listener tools
└── ui/
    ├── __init__.py
    └── main_window.py       # Main application window
```

## 🔄 Password Policy Notes

- **Default assumption**: 90-day password expiration policy
- **Domain policy detection**: Attempts to read actual domain policy settings
- **Fallback behavior**: Uses 90-day default if policy cannot be determined
- **Policy exceptions**: Properly handles accounts with password never expires flag
- **Disabled accounts**: Identifies and appropriately handles disabled user accounts
- **Compliance reporting**: Generates reports suitable for security audits

## 🤝 Contributing

Contributions are welcome! Priority areas for improvement:

### High Priority
- **Enhanced password policy detection** for accurate expiry calculations
- **Multi-domain support** for enterprise environments
- **Advanced reporting capabilities** with charts and graphs
- **Email notifications** for expiring passwords and service outages
- **REST API interface** for integration with other tools

### Medium Priority
- **Additional authentication methods** (Kerberos, certificate-based)
- **Advanced filtering and search** capabilities
- **Custom alerting rules** and thresholds
- **Integration with ticketing systems**
- **Mobile-responsive dashboard**

### Low Priority
- **Additional export formats** (PDF, Excel)
- **Historical trending** and analytics
- **Custom branding** and themes
- **Plugin architecture** for extensibility

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🚨 Disclaimer

This tool is provided as-is for IT infrastructure monitoring, security compliance, and troubleshooting purposes. Always:

### Security Responsibilities
- **Test thoroughly** in non-production environments first
- **Follow your organization's security policies** and procedures
- **Keep service account credentials secure** and rotate regularly
- **Monitor and audit** tool usage appropriately
- **Maintain compliance** with data protection regulations

### Operational Responsibilities
- **Verify results** against known good configurations
- **Document changes** made based on tool recommendations
- **Maintain backups** of configurations and reports
- **Regular updates** to keep security current

## 📞 Support

For issues and questions:

### Self-Help Resources
1. **Check troubleshooting section** above for common issues
2. **Review error messages** in console output with debug mode enabled
3. **Verify configuration** with test connection features
4. **Test with minimal setup** first before complex configurations

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and examples
- **Best Practices**: Security and operational guidelines

### Enterprise Support
For enterprise deployments requiring:
- **Custom integration** with existing systems
- **Advanced security** requirements and compliance
- **Dedicated support** and training
- **Custom feature development**

---

**SigmaToolkit v1.6.0** - Your comprehensive IT Swiss Army Knife for infrastructure monitoring, security compliance, and network diagnostics. Built for system administrators who demand efficiency, security, and reliability in their daily operations.