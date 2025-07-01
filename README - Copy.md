# SigmaToolkit

**Version: 1.5.0**

Sigma's IT Swiss Army Knife - A comprehensive PyQt5-based GUI application designed for system and network administrators to perform various IT troubleshooting tasks efficiently. Your all-in-one toolkit for daily IT operations and infrastructure monitoring.

## 🚀 Features

### 🟢 Service Monitor (v1.5.0) ✨ **NEW**
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

### 🛠️ General Features
- **Multi-Tab Interface**: Organized testing categories with clean navigation and Service Monitor priority
- **Debug Mode**: Toggle detailed logging for advanced troubleshooting
- **Real-time Output**: Live results with timestamp and color-coded log levels
- **Copy Results**: One-click copying of output to clipboard
- **Professional UI**: Modern interface designed for efficiency and infrastructure monitoring
- **Cross-Platform**: Works seamlessly on Windows, Linux, and macOS
- **Export Functionality**: Save analysis results, service reports, and configuration backups
- **Persistent Storage**: Auto-save configurations and settings