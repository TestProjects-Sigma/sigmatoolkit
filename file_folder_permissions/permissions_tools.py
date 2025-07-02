# file_folder_permissions/permissions_tools.py
"""
AD Folder Permissions Tools - Core functionality for scanning and analyzing folder permissions
"""

import os
import csv
import json
import subprocess
import threading
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal


class PermissionEntry:
    """Data class to represent a permission entry"""
    
    def __init__(self, path: str, identity: str, permission: str, 
                 access_type: str, inherited: bool = False):
        self.path = path
        self.identity = identity
        self.permission = permission
        self.access_type = access_type  # Allow/Deny
        self.inherited = inherited
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'Path': self.path,
            'Identity': self.identity,
            'Permission': self.permission,
            'Access Type': self.access_type,
            'Inherited': self.inherited,
            'Scan Time': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


class PermissionScanner:
    """Core class for scanning folder permissions using Windows tools"""
    
    @staticmethod
    def scan_folder_permissions(folder_path: str, include_subfolders: bool = False) -> List[PermissionEntry]:
        """Scan permissions for folders only using icacls command"""
        permissions = []
        
        try:
            # Normalize the path to use Windows backslashes
            normalized_path = os.path.normpath(folder_path)
            
            if include_subfolders:
                # First get all subdirectories
                subdirs = [normalized_path]
                try:
                    for root, dirs, files in os.walk(normalized_path):
                        for dir_name in dirs:
                            subdir_path = os.path.normpath(os.path.join(root, dir_name))
                            subdirs.append(subdir_path)
                except PermissionError:
                    print(f"Limited access during directory traversal")
                
                # Scan each directory individually
                for directory in subdirs:
                    dir_permissions = PermissionScanner._scan_single_folder(directory)
                    permissions.extend(dir_permissions)
            else:
                # Scan only the specified folder
                permissions = PermissionScanner._scan_single_folder(normalized_path)
        
        except Exception as e:
            print(f"Error scanning {folder_path}: {str(e)}")
            # Try alternative method
            return PermissionScanner._scan_with_powershell(folder_path, include_subfolders)
        
        print(f"Found {len(permissions)} total permission entries for folders")
        return permissions
    
    @staticmethod
    def _scan_single_folder(folder_path: str) -> List[PermissionEntry]:
        """Scan permissions for a single folder"""
        permissions = []
        
        try:
            # Normalize the path to use Windows backslashes
            normalized_path = os.path.normpath(folder_path)
            
            # Check if path exists first
            if not os.path.exists(normalized_path):
                print(f"Path does not exist: {normalized_path}")
                return permissions
            
            # Use icacls without quotes and without shell=True for better compatibility
            cmd = ['icacls', normalized_path]
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='cp1252', errors='replace')
            
            print(f"Scanning: {normalized_path}")
            print(f"Return code: {result.returncode}")
            
            if result.returncode != 0:
                print(f"icacls failed for {normalized_path}: {result.stderr}")
                # Try with PowerShell as fallback
                return PermissionScanner._scan_single_folder_powershell(normalized_path)
            
            # Parse icacls output
            lines = result.stdout.split('\n')
            
            for i, line in enumerate(lines):
                original_line = line
                line = line.strip()
                
                # Skip empty lines, status messages
                if not line or 'Successfully processed' in line or 'files processed' in line:
                    continue
                
                # Skip the first line (path line) or lines that start with the path
                if i == 0 or line.startswith(normalized_path):
                    continue
                
                # Look for permission entries - they should contain :( pattern
                if ':(' in line:
                    # Split by the first :( to get identity and permissions
                    colon_paren_pos = line.find(':(')
                    if colon_paren_pos > 0:
                        identity = line[:colon_paren_pos].strip()
                        permission_part = line[colon_paren_pos + 2:]  # Skip ':('
                        
                        print(f"Processing: Identity='{identity}', Permission part='{permission_part}'")
                        
                        # Extract all permission flags from the parentheses
                        import re
                        
                        # Find all parentheses content
                        paren_matches = re.findall(r'\(([^)]+)\)', permission_part)
                        print(f"Found parentheses content: {paren_matches}")
                        
                        if paren_matches:
                            # The actual permission is usually the last meaningful code
                            permission_codes = []
                            inherited = False
                            access_type = 'Allow'
                            
                            for match in paren_matches:
                                if match == 'I':
                                    inherited = True
                                elif match == 'DENY':
                                    access_type = 'Deny'
                                elif match in ['F', 'M', 'RX', 'R', 'W', 'D', 'C', 'RC', 'WD', 'AD', 'WEA', 'REA', 'X', 'DC']:
                                    # These are actual permission codes
                                    permission_codes.append(match)
                                # Skip inheritance flags like OI, CI, IO
                            
                            print(f"Permission codes found: {permission_codes}")
                            print(f"Inherited: {inherited}, Access type: {access_type}")
                            
                            if permission_codes:
                                # Use the permission codes to determine readable permissions
                                permission_code_str = ','.join(permission_codes)
                                readable_permissions = PermissionScanner._convert_to_readable_permissions(permission_code_str)
                                print(f"Readable permissions: '{readable_permissions}'")
                                
                                if identity and readable_permissions:
                                    permissions.append(PermissionEntry(
                                        path=normalized_path,
                                        identity=identity,
                                        permission=readable_permissions,
                                        access_type=access_type,
                                        inherited=inherited
                                    ))
                                    print(f"Added permission entry for {identity}")
            
            print(f"Total permissions found for {normalized_path}: {len(permissions)}")
        
        except Exception as e:
            print(f"Error scanning single folder {normalized_path}: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            # Fallback to PowerShell
            return PermissionScanner._scan_single_folder_powershell(normalized_path)
        
        return permissions
    
    @staticmethod
    def _scan_single_folder_powershell(folder_path: str) -> List[PermissionEntry]:
        """Scan a single folder using PowerShell as fallback"""
        permissions = []
        
        try:
            normalized_path = os.path.normpath(folder_path)
            print(f"Trying PowerShell fallback for: {normalized_path}")
            
            # PowerShell command for single folder
            ps_script = f"""
try {{
    $acl = Get-Acl -Path '{normalized_path}' -ErrorAction Stop
    foreach ($access in $acl.Access) {{
        $permissions = [System.Collections.Generic.List[string]]::new()
        
        # Check for specific permissions
        if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Read) {{ $permissions.Add("Read") }}
        if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Write) {{ $permissions.Add("Write") }}
        if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Modify) {{ $permissions.Add("Change") }}
        if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Delete) {{ $permissions.Add("Delete") }}
        if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::ReadAndExecute) {{ $permissions.Add("List") }}
        
        if ($permissions.Count -gt 0) {{
            $permString = $permissions -join ", "
            Write-Output "{normalized_path}|$($access.IdentityReference)|$permString|$($access.AccessControlType)|$($access.IsInherited)"
        }}
    }}
}} catch {{
    Write-Error "Failed to get ACL for {normalized_path}: $($_.Exception.Message)"
}}
"""
            
            cmd = ['powershell', '-Command', ps_script]
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='cp1252', errors='replace')
            
            print(f"PowerShell return code: {result.returncode}")
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if '|' in line and line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            path = parts[0].strip()
                            identity = parts[1].strip()
                            permission = parts[2].strip()
                            access_type = parts[3].strip()
                            inherited = parts[4].strip().lower() == 'true'
                            
                            if permission:  # Only add if we have readable permissions
                                permissions.append(PermissionEntry(
                                    path=path,
                                    identity=identity,
                                    permission=permission,
                                    access_type=access_type,
                                    inherited=inherited
                                ))
            else:
                if result.stderr:
                    print(f"PowerShell error: {result.stderr}")
        
        except Exception as e:
            print(f"PowerShell fallback error for {folder_path}: {str(e)}")
        
        return permissions
    
    @staticmethod
    def _scan_with_powershell(folder_path: str, include_subfolders: bool = False) -> List[PermissionEntry]:
        """Alternative scanning method using PowerShell - folders only"""
        permissions = []
        
        try:
            if include_subfolders:
                # PowerShell command to get ACL information for directories only
                ps_script = f"""
# Get all subdirectories
$folders = Get-ChildItem -Path '{folder_path}' -Recurse -Directory -ErrorAction SilentlyContinue
$folders += Get-Item -Path '{folder_path}' -ErrorAction SilentlyContinue

foreach ($folder in $folders) {{
    $path = $folder.FullName
    try {{
        $acl = Get-Acl -Path $path -ErrorAction Stop
        foreach ($access in $acl.Access) {{
            $permissions = [System.Collections.Generic.List[string]]::new()
            
            # Check for specific permissions
            if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Read) {{ $permissions.Add("Read") }}
            if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Write) {{ $permissions.Add("Write") }}
            if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Modify) {{ $permissions.Add("Change") }}
            if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Delete) {{ $permissions.Add("Delete") }}
            if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::ReadAndExecute) {{ $permissions.Add("List") }}
            
            if ($permissions.Count -gt 0) {{
                $permString = $permissions -join ", "
                Write-Output "$path|$($access.IdentityReference)|$permString|$($access.AccessControlType)|$($access.IsInherited)"
            }}
        }}
    }} catch {{
        # Skip inaccessible folders
    }}
}}
"""
            else:
                # PowerShell command for single folder
                ps_script = f"""
try {{
    $acl = Get-Acl -Path '{folder_path}' -ErrorAction Stop
    foreach ($access in $acl.Access) {{
        $permissions = [System.Collections.Generic.List[string]]::new()
        
        # Check for specific permissions
        if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Read) {{ $permissions.Add("Read") }}
        if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Write) {{ $permissions.Add("Write") }}
        if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Modify) {{ $permissions.Add("Change") }}
        if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::Delete) {{ $permissions.Add("Delete") }}
        if ($access.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::ReadAndExecute) {{ $permissions.Add("List") }}
        
        if ($permissions.Count -gt 0) {{
            $permString = $permissions -join ", "
            Write-Output "{folder_path}|$($access.IdentityReference)|$permString|$($access.AccessControlType)|$($access.IsInherited)"
        }}
    }}
}} catch {{
    # Skip if inaccessible
}}
"""
            
            cmd = ['powershell', '-Command', ps_script]
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='cp1252', errors='replace')
            
            print(f"PowerShell command executed, return code: {result.returncode}")
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if '|' in line and line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            path = parts[0].strip()
                            identity = parts[1].strip()
                            permission = parts[2].strip()
                            access_type = parts[3].strip()
                            inherited = parts[4].strip().lower() == 'true'
                            
                            if permission:  # Only add if we have readable permissions
                                permissions.append(PermissionEntry(
                                    path=path,
                                    identity=identity,
                                    permission=permission,
                                    access_type=access_type,
                                    inherited=inherited
                                ))
        
        except Exception as e:
            print(f"PowerShell scan error: {str(e)}")
        
        return permissions
    
    @staticmethod
    def _convert_to_readable_permissions(permission_code: str) -> str:
        """Convert icacls permission codes to readable permission types"""
        readable_permissions = []
        
        # Handle comma-separated codes
        codes = [code.strip().upper() for code in permission_code.split(',')]
        
        print(f"Converting permission codes: {codes}")
        
        # Check for Full Control first
        if any(code in ['F', 'FC', 'FULLCONTROL'] for code in codes):
            return "Read, Write, Change, Delete, List"
        
        # Check for Modify
        if any(code in ['M', 'MODIFY'] for code in codes):
            return "Read, Write, Change, Delete, List"
        
        # Check individual permissions
        has_read = any(code in ['R', 'RX', 'RC', 'GR', 'RD'] for code in codes)
        has_write = any(code in ['W', 'WD', 'AD', 'WEA', 'GW'] for code in codes)
        has_execute = any(code in ['RX', 'X', 'GE'] for code in codes)
        has_delete = any(code in ['D', 'DC', 'DA'] for code in codes)
        
        # RX typically means Read & Execute (which includes List)
        if any(code in ['RX'] for code in codes):
            has_read = True
            has_execute = True
        
        # Build readable permissions
        if has_read:
            readable_permissions.append("Read")
        if has_write:
            readable_permissions.append("Write")
        if has_write or any(code in ['M', 'MODIFY'] for code in codes):  # Modify implies Change
            if "Change" not in readable_permissions:
                readable_permissions.append("Change")
        if has_delete:
            readable_permissions.append("Delete")
        if has_execute or has_read:  # Execute or Read typically includes List
            if "List" not in readable_permissions:
                readable_permissions.append("List")
        
        result = ', '.join(readable_permissions) if readable_permissions else ""
        print(f"Converted '{permission_code}' to '{result}'")
        return result
    
    @staticmethod
    def is_ad_group(identity: str) -> bool:
        """Check if identity is likely an AD group (basic heuristic)"""
        ad_indicators = ['DOMAIN\\', 'BUILTIN\\', '\\Domain', '\\']
        return any(indicator in identity.upper() for indicator in ad_indicators)


class ScanWorker(QThread):
    """Worker thread for scanning permissions"""
    
    progress = pyqtSignal(str)  # Status message
    finished = pyqtSignal(list)  # List of PermissionEntry objects
    error = pyqtSignal(str)  # Error message
    
    def __init__(self, paths: List[str], include_subfolders: bool = True):
        super().__init__()
        self.paths = paths
        self.include_subfolders = include_subfolders
        self.scanner = PermissionScanner()
    
    def run(self):
        """Run the scanning process"""
        all_permissions = []
        
        try:
            for path in self.paths:
                self.progress.emit(f"Scanning: {path}")
                
                # Check if path exists
                if not os.path.exists(path):
                    self.error.emit(f"Path not found: {path}")
                    continue
                
                # Check if we can access the path
                try:
                    os.listdir(path) if os.path.isdir(path) else os.path.exists(path)
                    self.progress.emit(f"Path accessible, scanning permissions...")
                except PermissionError:
                    self.progress.emit(f"Limited access to path, attempting permission scan anyway...")
                
                permissions = self.scanner.scan_folder_permissions(path, self.include_subfolders)
                all_permissions.extend(permissions)
                
                self.progress.emit(f"Found {len(permissions)} permission entries in {path}")
            
            self.finished.emit(all_permissions)
        
        except Exception as e:
            self.error.emit(f"Scanning error: {str(e)}")
            import traceback
            print(f"Full error trace: {traceback.format_exc()}")


class PermissionsTools:
    """Main class for permission analysis tools"""
    
    def __init__(self, logger):
        self.logger = logger
        self.permissions_data = []
    
    def scan_folder_permissions_async(self, paths: List[str], include_subfolders: bool, 
                                    progress_callback, finished_callback, error_callback):
        """Start async permission scanning"""
        self.scan_worker = ScanWorker(paths, include_subfolders)
        self.scan_worker.progress.connect(progress_callback)
        self.scan_worker.finished.connect(finished_callback)
        self.scan_worker.error.connect(error_callback)
        self.scan_worker.start()
        return self.scan_worker
    
    def filter_permissions(self, permissions: List[PermissionEntry], 
                         filter_text: str = "", show_ad_only: bool = False) -> List[PermissionEntry]:
        """Filter permissions based on criteria"""
        filtered = permissions
        
        # Apply AD groups filter
        if show_ad_only:
            filtered = [p for p in filtered if PermissionScanner.is_ad_group(p.identity)]
        
        # Apply search filter
        if filter_text:
            filter_text = filter_text.lower()
            filtered = [
                p for p in filtered 
                if filter_text in p.identity.lower() or 
                   filter_text in p.path.lower() or
                   filter_text in p.permission.lower()
            ]
        
        return filtered
    
    def export_to_csv(self, permissions: List[PermissionEntry], filename: str) -> bool:
        """Export permissions to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Path', 'Identity', 'Permission', 'Access Type', 'Inherited', 'Scan Time']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for perm in permissions:
                    writer.writerow(perm.to_dict())
            
            self.logger.success(f"Exported {len(permissions)} entries to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export to CSV: {str(e)}")
            return False
    
    def export_to_json(self, permissions: List[PermissionEntry], filename: str) -> bool:
        """Export permissions to JSON file"""
        try:
            data = {
                'scan_info': {
                    'scan_date': datetime.now().isoformat(),
                    'total_entries': len(permissions)
                },
                'permissions': [perm.to_dict() for perm in permissions]
            }
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
            self.logger.success(f"Exported {len(permissions)} entries to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export to JSON: {str(e)}")
            return False
    
    def get_summary_stats(self, permissions: List[PermissionEntry]) -> Dict:
        """Get summary statistics for permissions"""
        if not permissions:
            return {
                'total_entries': 0,
                'unique_paths': 0,
                'unique_identities': 0,
                'ad_groups': 0,
                'inherited_permissions': 0,
                'explicit_permissions': 0,
                'deny_permissions': 0
            }
        
        unique_paths = set(p.path for p in permissions)
        unique_identities = set(p.identity for p in permissions)
        ad_groups = [p for p in permissions if PermissionScanner.is_ad_group(p.identity)]
        inherited = [p for p in permissions if p.inherited]
        explicit = [p for p in permissions if not p.inherited]
        deny_perms = [p for p in permissions if p.access_type.lower() == 'deny']
        
        return {
            'total_entries': len(permissions),
            'unique_paths': len(unique_paths),
            'unique_identities': len(unique_identities),
            'ad_groups': len(ad_groups),
            'inherited_permissions': len(inherited),
            'explicit_permissions': len(explicit),
            'deny_permissions': len(deny_perms)
        }