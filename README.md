# SigmaToolkit

**Version: 1.1.0**

Sigma's IT Swiss Army Knife - A comprehensive PyQt5-based GUI application designed for system and network administrators to perform various IT troubleshooting tasks efficiently. Your all-in-one toolkit for daily IT operations.

## Features

### Network Testing (v1.0.0)
- **Ping Test**: Test connectivity to hosts with customizable packet count
- **Traceroute**: Trace network path to destination hosts
- **Port Scanner**: Scan single ports, port ranges, or comma-separated port lists
- **DNS Lookup**: Basic forward and reverse DNS lookups
- **Quick Actions**: One-click tests for common DNS servers and default gateway

### DNS Testing (v1.1.0)
- **Forward/Reverse Lookup**: Domain ↔ IP address resolution
- **MX Records**: Mail server configuration analysis
- **TXT Records**: SPF, DKIM, and other text records for email authentication
- **NS Records**: Name server information and delegation
- **CNAME Records**: Domain aliases and canonical names
- **AAAA Records**: IPv6 address resolution
- **DNS Server Selection**: Test with Google, Cloudflare, Quad9, or custom DNS servers
- **Comprehensive Analysis**: All-in-one DNS record lookup

### General Features
- **Multi-Tab Interface**: Organized testing categories with clean navigation
- **Debug Mode**: Toggle detailed logging for advanced troubleshooting
- **Real-time Output**: Live results with timestamp and color-coded log levels
- **Copy Results**: One-click copying of output to clipboard
- **Professional UI**: Modern interface designed for efficiency
- **Cross-Platform**: Works seamlessly on Windows, Linux, and macOS

## Installation

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
- requests==2.31.0 (for future web-based tests)

## Project Structure

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
└── ui/
    ├── __init__.py
    └── main_window.py     # Main application window
```

## Usage Guide

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

#### Quick Test Domains
- One-click testing of major domains (Google, Microsoft, GitHub)
- Local domain detection and testing

### 📊 Output Window Controls
- **Clear Output**: Remove all logged results
- **Copy Output**: Copy all results to clipboard for reports
- **Toggle Debug**: Enable/disable detailed debug information

## Keyboard Shortcuts

- `Ctrl+Q`: Quit application
- `Enter`: Execute test in focused input field

## Configuration

Settings are automatically saved to:
- **Windows**: `%USERPROFILE%\.SigmaToolkit\settings.json`
- **Linux/macOS**: `~/.SigmaToolkit/settings.json`

Configuration includes:
- Window geometry and preferences
- Default test parameters
- Favorite hosts and domains
- Debug mode settings

## Version History

### v1.1.0 (Current) - DNS Analysis
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

## Planned Enhancements

### v1.2.0 - Email & Communication Testing
- SMTP connection testing and authentication
- Email delivery verification and diagnostics
- SSL/TLS certificate analysis
- Mail server security assessment

### v1.3.0 - System Monitoring & Analysis
- CPU, memory, and disk usage monitoring
- Service status verification and management
- System performance diagnostics
- Resource usage alerts and logging

### v1.4.0 - Advanced Network Analysis
- Advanced port scanning with service detection
- Bandwidth testing and network performance
- SSL/TLS certificate verification and analysis
- Network security scanning capabilities

## Troubleshooting

### Common Issues

1. **"Command not found" errors**:
   - Ensure system has ping/traceroute/nslookup tools installed
   - On Windows, verify Command Prompt tools are available in PATH
   - On Linux/macOS, install: `sudo apt-get install dnsutils` (Ubuntu) or equivalent

2. **DNS lookup failures**:
   - Try different DNS servers from the dropdown
   - Check network connectivity with ping tests first
   - Verify domain names are spelled correctly

3. **Port scanning appears slow**:
   - Large port ranges (1-65535) take considerable time
   - Use debug mode to monitor scanning progress
   - Consider smaller ranges or specific ports for faster results

4. **Permission errors**:
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

## Best Practices

### For System Administrators
- **Start with basic connectivity** (ping) before advanced tests
- **Use debug mode** when troubleshooting complex network issues
- **Test with multiple DNS servers** to identify DNS-specific problems
- **Copy results to clipboard** for documentation and reports
- **Regular testing** of critical infrastructure with quick action buttons

### Security Considerations
- **Port scanning**: Only scan systems you own or have permission to test
- **DNS testing**: Be aware that extensive DNS queries may be logged
- **Network analysis**: Follow your organization's security policies
- **Result sharing**: Be cautious when sharing output that may contain sensitive information

## License

SigmaToolkit is created for system administrators to enhance their daily workflow. Use responsibly and in accordance with your organization's policies and applicable laws.

## Contributing

This tool is designed with modularity in mind. The clean OOP structure makes it easy to:
- Add new testing tabs
- Extend existing functionality
- Integrate with other tools
- Customize for specific environments

## Support

For issues, feature requests, or troubleshooting:
1. Check the debug output for detailed error information
2. Verify your system has the required network tools installed
3. Test with known-good targets to isolate the issue
4. Document any error messages and steps to reproduce

---

**SigmaToolkit v1.1.0** - Your comprehensive IT Swiss Army knife for efficient network and DNS troubleshooting.

*Built by system administrators, for system administrators.*