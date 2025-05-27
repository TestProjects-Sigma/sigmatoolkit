# SigmaToolkit

**Version: 1.4.0**

Sigma's IT Swiss Army Knife - A comprehensive PyQt5-based GUI application designed for system and network administrators to perform various IT troubleshooting tasks efficiently. Your all-in-one toolkit for daily IT operations.

## 🚀 Features

### 🌐 Network Testing (v1.0.0)
- **Ping Test**: Test connectivity to hosts with customizable packet count
- **Traceroute**: Trace network path to destination hosts
- **Port Scanner**: Scan single ports, port ranges, or comma-separated port lists
- **DNS Lookup**: Basic forward and reverse DNS lookups
- **Quick Actions**: One-click tests for common DNS servers and default gateway

### 🔍 DNS Testing (v1.1.0)
- **Forward/Reverse Lookup**: Domain ↔ IP address resolution
- **MX Records**: Mail server configuration analysis
- **TXT Records**: SPF, DKIM, and other text records for email authentication
- **NS Records**: Name server information and delegation
- **CNAME Records**: Domain aliases and canonical names
- **AAAA Records**: IPv6 address resolution
- **DNS Server Selection**: Test with Google, Cloudflare, Quad9, or custom DNS servers
- **Comprehensive Analysis**: All-in-one DNS record lookup

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

### 📨 Mail Header Analysis (v1.4.0) ✨ **NEW**
- **Comprehensive Header Analysis**: Parse and analyze email headers with detailed insights
- **Email Authentication Verification**: Complete SPF, DKIM, and DMARC validation
- **Delivery Path Tracking**: Trace email route with timestamps and delay analysis
- **Spam Detection**: IP reputation checking and suspicious pattern identification
- **Interactive Analysis**: Multiple tabs for different analysis types
- **Security Assessment**: Identify potential spoofing and phishing indicators
- **Export Capabilities**: Save analysis results for documentation and reports
- **Sample Headers**: Built-in examples for testing and learning

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
- **Multi-Tab Interface**: Organized testing categories with clean navigation
- **Debug Mode**: Toggle detailed logging for advanced troubleshooting
- **Real-time Output**: Live results with timestamp and color-coded log levels
- **Copy Results**: One-click copying of output to clipboard
- **Professional UI**: Modern interface designed for efficiency
- **Cross-Platform**: Works seamlessly on Windows, Linux, and macOS
- **Export Functionality**: Save analysis results and reports

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Quick Setup
1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run SigmaToolkit**:
   ```bash
   python main.py
   ```

### Dependencies
- PyQt5==5.15.10
- python-nmap==0.7.1 (for future advanced port scanning)
- requests==2.31.0 (for network testing and web requests)
- speedtest-cli==2.1.3 (for accurate speed testing)

### Optional: Install Speedtest CLI for Accurate Results
For the most accurate gigabit speed testing, install speedtest CLI:

**Windows:**
```bash
# Option 1: Python version (recommended)
pip install speedtest-cli

# Option 2: Official CLI
# Download from: https://www.speedtest.net/apps/cli

# Option 3: Package manager
choco install speedtest
```

**Linux:**
```bash
# Option 1: Python version
sudo apt install speedtest-cli
# or
pip install speedtest-cli

# Option 2: Official Ookla CLI
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest
```

**macOS:**
```bash
# Option 1: Homebrew
brew install speedtest-cli

# Option 2: Python version
pip install speedtest-cli
```

## 📁 Project Structure

```
SigmaToolkit/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This documentation
├── config/
│   └── settings.py        # Configuration management
├── core/
│   ├── __init__.py
│   ├── base_tab.py       # Base class for all tabs
│   └── logger.py         # Logging system
├── network/
│   ├── __init__.py
│   ├── network_tab.py    # Network testing UI
│   └── network_tools.py  # Network testing logic
├── dns/
│   ├── __init__.py
│   ├── dns_tab.py        # DNS testing UI
│   └── dns_tools.py      # DNS testing logic
├── smtp/
│   ├── __init__.py
│   ├── smtp_tab.py       # SMTP testing UI
│   └── smtp_tools.py     # SMTP testing logic
├── speedtest/
│   ├── __init__.py
│   ├── speedtest_tab.py    # Speed testing UI
│   └── speedtest_tools.py  # Speed testing logic
├── mail/                   # NEW in v1.4.0
│   ├── __init__.py
│   ├── mail_tab.py        # Mail header analysis UI
│   └── mail_tools.py      # Mail analysis logic
└── ui/
    ├── __init__.py
    └── main_window.py     # Main application window
```

## 📖 Usage Guide

### 🌐 Network Testing Tab

#### Ping Test
1. Enter hostname or IP address (e.g., `google.com` or `8.8.8.8`)
2. Set packet count (1-100, default: 4)
3. Click "Ping" or press Enter
4. Results appear in the output window with success/failure status

#### Traceroute
1. Enter hostname or IP address
2. Click "Traceroute" or press Enter
3. View the complete network path and hop-by-hop latency

#### Port Scanner
1. Enter target hostname or IP address
2. Enter ports to scan:
   - Single port: `80`
   - Multiple ports: `80,443,22`
   - Port range: `1-1000`
3. Click "Scan Ports"
4. Open ports highlighted in green, summary provided

#### Quick Actions
- **Ping Google DNS**: Test connectivity to 8.8.8.8
- **Ping Cloudflare DNS**: Test connectivity to 1.1.1.1
- **Ping Gateway**: Automatically detect and ping default gateway

### 🔍 DNS Testing Tab

#### Quick DNS Lookups
- **Forward Lookup**: Convert domain names to IP addresses
- **Reverse Lookup**: Convert IP addresses back to domain names
- **All Records**: Comprehensive DNS analysis of a domain

#### Specific Record Analysis
- **MX Records**: Mail server configuration for email troubleshooting
- **TXT Records**: SPF/DKIM records for email authentication verification
- **NS Records**: Name server delegation and DNS infrastructure
- **CNAME Records**: Domain aliases and redirection analysis
- **AAAA Records**: IPv6 address resolution

#### DNS Server Testing
- Test resolution using different DNS providers
- Compare results across Google DNS, Cloudflare, Quad9
- Use custom DNS servers for specific testing scenarios

### 📧 SMTP Testing Tab

#### Server Configuration
- **Server Settings**: Enter SMTP server address and port
- **Encryption Options**: Choose between TLS (STARTTLS) or SSL encryption
- **Timeout Control**: Configure connection timeout (5-60 seconds)

#### Authentication Options
- **Optional Authentication**: Leave username/password empty for relay testing
- **Credential Testing**: Test username and password authentication when provided
- **Relay Mode**: Test internal mail servers without authentication requirements
- **Smart Error Handling**: Helpful suggestions for authentication failures

#### Email Testing
- **Test Email Sending**: Send actual test emails with customizable content
- **Relay Support**: Send emails through open relay servers (no auth required)
- **Delivery Confirmation**: Verify successful email transmission
- **Custom Recipients**: Configure sender and recipient addresses
- **Authentication Status**: Email body shows whether auth was used or relay mode

#### Quick Server Presets
- **Gmail**: Pre-configured Gmail SMTP settings (smtp.gmail.com:587)
- **Outlook.com**: Microsoft consumer email settings
- **Office 365**: Microsoft business email configuration
- **Yahoo**: Yahoo Mail SMTP settings
- **Clear All**: Reset all fields for custom configuration

#### Advanced Features
- **MX Record Integration**: Check domain mail server configuration
- **Comprehensive Testing**: All-in-one SMTP analysis with sequential tests
- **Auto-fill Features**: Smart form completion based on email addresses

### ⚡ Speed Testing Tab

#### Official Speedtest.net Integration
- **🚀 Official Speedtest Button**: Uses genuine speedtest.net CLI for maximum accuracy
- **Automatic CLI Detection**: Intelligently detects official Ookla CLI or Python speedtest-cli
- **Gigabit-Optimized**: Specifically designed to handle high-speed fiber connections
- **Real Results**: Same engine as speedtest.net website for trusted measurements

#### Professional Speed Analysis
- **LCD-Style Displays**: Live readouts for download speed, upload speed, and latency
- **Progress Tracking**: Real-time progress bars with detailed status updates
- **Visual Feedback**: Color-coded displays (green for download, orange for upload, blue for latency)
- **Quality Assessment**: Automatic performance grading (Excellent/Good/Fair/Poor)

#### Comprehensive Testing Options
- **🔧 Test CLI**: Manual speedtest CLI testing and debugging
- **📥 Install CLI**: Step-by-step installation guidance for speedtest tools
- **List Servers**: Browse available speedtest servers and select optimal locations
- **Fallback Tests**: Built-in safe testing when CLI is unavailable

#### Advanced Features
- **Multi-CLI Support**: Works with both official Ookla CLI and Python speedtest-cli versions
- **Intelligent Server Selection**: Auto-detect best servers or manually choose specific locations
- **Error Handling**: Detailed troubleshooting and helpful error messages
- **Installation Helper**: Built-in guidance for Windows, Linux, and macOS CLI setup
- **Safe Operation**: Timer-based fallback tests that won't crash the application

#### For Gigabit Connections
- **Accurate High-Speed Testing**: Properly measures 500+ Mbps connections
- **Fiber-Optimized Protocol**: Uses speedtest.net's proven high-bandwidth testing
- **Multiple Server Options**: Test with different CDN providers for validation
- **Real-World Results**: Matches commercial speedtest tools and ISP measurements

#### Quick Test Domains
- One-click testing of major domains (Google, Microsoft, GitHub)
- Local domain detection and testing

### 📨 Mail Header Analysis Tab ✨ **NEW**

#### Header Analysis
1. **Input Email Headers**:
   - Copy headers from email client's "View Source" or "Show Original"
   - Paste directly into the text area
   - Or use "Load Sample" to test with example headers

2. **Analyze Headers**:
   - Click "🔍 Analyze Headers" for comprehensive analysis
   - View parsed headers in organized tree view
   - Read quick summary and detailed analysis

3. **Export Results**:
   - Use "💾 Export Results" to save analysis to file
   - Perfect for documentation and troubleshooting reports

#### Email Authentication Analysis
1. **Domain Setup**:
   - Enter domain from email headers (auto-extracted)
   - Optionally add sender IP for SPF validation

2. **Individual Checks**:
   - **🛡️ Check SPF**: Validate sender policy framework
   - **🔑 Check DKIM**: Verify digital signatures and keys
   - **📋 Check DMARC**: Analyze domain authentication policies

3. **Comprehensive Analysis**:
   - Use "🔒 Full Auth Analysis" for complete security assessment
   - Get recommendations for improving email security

#### Delivery Path Analysis
1. **Automatic Detection**: Headers are automatically analyzed for delivery path
2. **Customizable Display**:
   - Toggle timestamps, delays, server info
   - Reverse order for chronological viewing
   - Calculate total delivery time and identify bottlenecks

3. **Statistics**: View delivery stats including hop count and timing analysis

#### Spam Analysis
1. **IP Reputation**: Check sender IP against reputation databases
2. **Blacklist Verification**: Test IP against common spam blacklists
3. **Content Analysis**: Identify suspicious patterns and indicators
4. **Overall Assessment**: Get spam probability and risk scores

#### Mail Analysis Tips
- **Copy headers exactly** from email client's raw view
- **Use comprehensive analysis** for complete email diagnostics
- **Combine with SMTP testing** for end-to-end email troubleshooting
- **Export results** for sharing with team or documentation
- **Check authentication** regularly to ensure email security compliance

### 📊 Output Window Controls
- **Clear Output**: Remove all logged results
- **Copy Output**: Copy all results to clipboard for reports
- **Toggle Debug**: Enable/disable detailed debug information

## ⌨️ Keyboard Shortcuts

- `Ctrl+Q`: Quit application
- `Enter`: Execute test in focused input field

## ⚙️ Configuration

Settings are automatically saved to:
- **Windows**: `%USERPROFILE%\.SigmaToolkit\settings.json`
- **Linux/macOS**: `~/.SigmaToolkit/settings.json`

Configuration includes:
- Window geometry and preferences
- Default test parameters
- Favorite hosts and domains
- Debug mode settings

## 📋 Version History

### v1.4.0 (Current) - Mail Header Analysis & Security
- **NEW**: Comprehensive mail header analysis tab with multiple analysis types
- Email header parsing with detailed breakdown and security assessment
- SPF/DKIM/DMARC authentication verification with policy analysis
- Email delivery path tracking with timestamp and delay analysis
- Spam detection with IP reputation checking and blacklist verification
- Interactive analysis interface with tree view and tabbed organization
- Export functionality for analysis results and troubleshooting reports
- Integration with existing SMTP testing for complete email diagnostics workflow

### v1.3.0 - Network Performance & Speed Testing
- **NEW**: Comprehensive speed testing tab with real-time visual displays
- Internet speed testing with download/upload bandwidth measurement
- Latency analysis with jitter calculation and quality assessment
- LAN speed testing for local network performance analysis
- Multiple test server options (Cloudflare, Google, Microsoft, GitHub, Ubuntu)
- Real-time LCD-style speed displays with color-coded feedback
- Progress monitoring with configurable test durations
- Network device detection and auto-discovery features
- Comprehensive testing workflows for complete network analysis

### v1.2.0 - SMTP Email Testing
- **NEW**: Comprehensive SMTP testing tab with full email server analysis
- SMTP server connection testing with TLS/SSL support
- Email authentication verification with detailed error reporting
- Test email sending with delivery confirmation
- SMTP port scanning and server capability detection
- Quick presets for major email providers (Gmail, Outlook, Office 365, Yahoo)
- MX record integration for complete email troubleshooting workflow
- Auto-fill features and smart form completion

### v1.1.0 - DNS Analysis
- **NEW**: Comprehensive DNS testing tab
- MX, TXT, NS, CNAME, AAAA record lookups
- DNS server selection and comparison
- SPF/DKIM analysis for email authentication
- Quick test domains and troubleshooting guidance

### v1.0.0 - Network Foundation
- Initial release with network testing capabilities
- Ping, traceroute, port scanning, basic DNS lookup
- Debug logging system and output management
- Cross-platform compatibility
- Clean PyQt5 interface with professional styling

## 🔮 Planned Enhancements

### v1.5.0 - Advanced Email Security & Forensics
- Enhanced mail header forensics with threat intelligence integration
- Advanced SPF/DKIM/DMARC policy simulation and testing
- Email authentication bypass detection and security recommendations
- Bulk email header analysis with batch processing capabilities
- Integration with external threat intelligence feeds

### v1.6.0 - Remote Access & Management
- Built-in SSH terminal with connection management
- Saved connection profiles and credential management
- Remote command execution and automation
- Secure file transfer capabilities (SCP/SFTP)

### v2.0.0 - System Monitoring & Advanced Analysis
- CPU, memory, and disk usage monitoring
- System performance diagnostics and alerting
- Advanced packet capture and protocol analysis
- Network security scanning and vulnerability assessment

## 🛠️ Troubleshooting

### Common Issues

1. **"Command not found" errors**:
   - Ensure system has ping/traceroute/nslookup tools installed
   - On Windows, verify Command Prompt tools are available in PATH
   - On Linux/macOS, install: `sudo apt-get install dnsutils` (Ubuntu) or equivalent

2. **DNS lookup failures**:
   - Try different DNS servers from the dropdown
   - Check network connectivity with ping tests first
   - Verify domain names are spelled correctly

3. **SMTP connection failures**:
   - Verify server address and port are correct
   - Check if TLS/SSL settings match server requirements
   - Ensure firewall allows outbound connections on SMTP ports
   - Try different ports (587 for TLS, 465 for SSL, 25 for plain)

4. **SMTP authentication errors**:
   - Verify username and password are correct
   - Check if 2-factor authentication requires app-specific passwords
   - Ensure account has SMTP access enabled
   - Some providers require "less secure app access" to be enabled

5. **Email sending failures**:
   - Verify both 'From' and 'To' email addresses are valid
   - Check if sender domain matches authentication credentials
   - Ensure recipient email address accepts external emails
   - Test with a known working recipient address first

6. **Port scanning appears slow**:
   - Large port ranges (1-65535) take considerable time
   - Use debug mode to monitor scanning progress
   - Consider smaller ranges or specific ports for faster results

7. **Speed test inaccuracies**:
   - Close all other applications using internet bandwidth
   - Ensure no background downloads, updates, or streaming are running
   - Use longer test durations (30-60 seconds) for more accurate results
   - Test with multiple servers to identify potential server-side limitations
   - Check if antivirus or firewall is interfering with tests
   - For gigabit connections, try custom servers closer to your location

8. **Mail header analysis issues**:
   - Ensure you're copying complete headers from email client
   - Use "View Source" or "Show Original" option in email client
   - Check that headers include "Received:" lines for delivery path analysis
   - Verify domain names are correct for authentication checks

9. **Permission errors**:
    - Some network tools may require elevated privileges
    - Run as administrator (Windows) or with sudo (Linux/macOS) if needed
    - ICMP ping may require root privileges on some systems

### Debug Mode
Enable debug mode for detailed logging of all operations:
- Click "Toggle Debug" button in the output section
- View detailed information about each network operation
- Useful for diagnosing connectivity issues and tool behavior
- All debug information is timestamped and categorized

### Getting Help
1. **Check the output window** for specific error messages
2. **Enable debug mode** for detailed operation logs
3. **Test with known-good targets** (like Google DNS) to isolate issues
4. **Verify network connectivity** before advanced testing
5. **Use sample data** in mail analysis to test functionality

## 💡 Best Practices

### Mail Header Analysis Workflow
1. **Start with header analysis**: Get overall email assessment and identify potential issues
2. **Check authentication**: Verify SPF/DKIM/DMARC status for security compliance
3. **Analyze delivery path**: Identify routing issues and delivery delays
4. **Check spam indicators**: Assess reputation and blacklist status
5. **Export results**: Document findings for team collaboration and compliance

### Email Security Assessment Workflow
1. **Domain verification**: Ensure proper SPF records are configured
2. **DKIM validation**: Verify cryptographic signatures and key strength
3. **DMARC policy review**: Check alignment settings and failure policies
4. **IP reputation check**: Validate sender IP against blacklists
5. **Header forensics**: Look for spoofing attempts and suspicious patterns

### Speed Testing Workflow
1. **Install speedtest CLI**: Use `pip install speedtest-cli` for accurate results
2. **Use "🚀 Official Speedtest"**: For real gigabit fiber speed measurements
3. **Test multiple servers**: Validate results across different server locations
4. **Check "🔧 Test CLI"**: If official test fails, debug with manual CLI testing
5. **Built-in tests**: Only use as safe fallbacks - they show simulated lower speeds
6. **Document baselines**: Record normal speeds for future comparison and troubleshooting

### Network Performance Troubleshooting Workflow
1. **Start with latency testing**: Check ping times and jitter to identify connection quality
2. **Test download speeds**: Measure bandwidth availability for incoming data
3. **Test upload speeds**: Verify outbound bandwidth capabilities
4. **Use comprehensive tests**: For complete network performance analysis
5. **Compare multiple servers**: Identify if issues are server-specific or general
6. **Document baseline performance**: Establish normal speeds for comparison

### For System Administrators
- **Start with basic connectivity** (ping) before advanced tests
- **Use DNS testing** to verify domain configuration before SMTP testing
- **Test SMTP connectivity** before attempting authentication
- **Use "🚀 Official Speedtest"** for accurate gigabit speed measurements
- **Install speedtest CLI** for maximum accuracy: `pip install speedtest-cli`
- **Baseline network performance** with speed tests for future troubleshooting
- **Use mail header analysis** for email security audits and compliance
- **Check email authentication** regularly to prevent spoofing and phishing
- **Use debug mode** when troubleshooting complex network or email issues
- **Test with multiple DNS servers** to identify DNS-specific problems
- **Verify MX records** before testing SMTP servers
- **Use comprehensive tests** for complete server analysis
- **Copy results to clipboard** for documentation and reports
- **Export analysis results** for compliance and security reporting
- **Regular testing** of critical infrastructure with quick action buttons

### Email Troubleshooting Workflow
1. **Check DNS first**: Verify domain has MX records
2. **Test SMTP connectivity**: Ensure mail server is reachable
3. **Verify authentication**: Test credentials and auth methods
4. **Send test email**: Confirm end-to-end email delivery
5. **Analyze headers**: Check delivery path and authentication status
6. **Document results**: Copy output for troubleshooting records

### Security Considerations
- **Port scanning**: Only scan systems you own or have permission to test
- **DNS testing**: Be aware that extensive DNS queries may be logged
- **SMTP testing**: Only test with accounts you own or have authorization to use
- **Email sending**: Be responsible when sending test emails to avoid spam complaints
- **Mail analysis**: Handle email headers containing PII with appropriate care
- **Authentication testing**: Use dedicated test accounts when possible
- **Credentials**: Never use production passwords in testing environments
- **Speed testing**: Speedtest traffic may be monitored or throttled by some ISPs
- **Network analysis**: Follow your organization's security policies
- **Result sharing**: Be cautious when sharing output that may contain sensitive information
- **Authentication**: Use app-specific passwords when available instead of account passwords

## 📄 License

SigmaToolkit is created for system administrators to enhance their daily workflow. Use responsibly and in accordance with your organization's policies and applicable laws.

## 🤝 Contributing

SigmaToolkit is designed with modularity and extensibility in mind. The clean OOP structure makes it easy to:

### Adding New Features
- **New testing tabs**: Follow the BaseTab pattern for consistent integration
- **Extend existing functionality**: Add methods to existing tool classes
- **Integrate with other tools**: Use the established signal/slot pattern for UI updates
- **Custom protocols**: Add new network testing protocols following existing patterns

### Code Structure
- **BaseTab class**: Inherit from this for all new testing tabs
- **Tool classes**: Separate business logic from UI components
- **Signal-based communication**: Use PyQt signals for thread-safe UI updates
- **Modular design**: Each testing category is self-contained and independent

### Development Guidelines
- **Follow PEP 8**: Python style guidelines for consistent code
- **Error handling**: Comprehensive try-catch blocks with user-friendly messages
- **Threading safety**: Use QTimer or proper signal/slot patterns for UI updates
- **Cross-platform**: Test on Windows, Linux, and macOS when possible
- **Documentation**: Update README.md with new features and version changes

### Future Enhancement Ideas
- **Advanced mail security**: Threat intelligence integration and security scoring
- **SSH terminal integration**: Built-in secure shell connectivity
- **System monitoring**: CPU, memory, and disk usage monitoring
- **Certificate analysis**: SSL/TLS certificate validation and inspection
- **Packet capture**: Basic network packet analysis capabilities

## 📞 Support

For issues, feature requests, or troubleshooting:
1. Check the debug output for detailed error information
2. Verify your system has the required network tools installed
3. Test with known-good targets to isolate the issue
4. Document any error messages and steps to reproduce

---

**SigmaToolkit v1.4.0** - Your comprehensive IT Swiss Army knife for efficient network, DNS, email, speed, and mail header analysis troubleshooting.

*Built by system administrators, for system administrators.*