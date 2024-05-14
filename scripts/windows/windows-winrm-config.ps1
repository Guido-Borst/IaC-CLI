$ErrorActionPreference = "SilentlyContinue"
$ErrorActionPreference = "Stop"

#Start-Transcript C:\configure_winrm.txt

try{
    # Set network profile to PRIVATE. Required since the WinRM config 
    # below will error out if a network profile is set to PUBLIC. 
    Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private
    
    # Enable and allow WinRM traffic through Windows Firewall 
    netsh advfirewall firewall set rule group="Windows Remote Management" new enable=yes
    netsh advfirewall firewall set rule name="Windows Remote Management (HTTP-In)" new enable=yes action=allow

    # Configure WinRM (Do not modify syntax as it breaks WinRM)
    winrm quickconfig -q
    winrm set winrm/config/service '@{AllowUnencrypted="true"}'
    winrm set winrm/config/service/auth '@{Basic="true"}'
    winrm set winrm/config/client/auth '@{Basic="true"}'
    winrm set winrm/config '@{MaxTimeoutms="7200000"}'
    winrm set winrm/config/winrs '@{IdleTimeout="7200000"}'
    winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="2048"}'
    winrm set winrm/config/service '@{MaxConcurrentOperationsPerUser="12000"}'

    # Making double sure WinRM service is set to auto.
    Stop-Service WinRM
    Set-Service -Name WinRM -StartupType Automatic
    Start-Service WinRM
    
    # Disable Windows firewall as I am running into an issue where 
    # the network profile gets reset to PUBLIC after a reboot.
    netsh advfirewall set allprofiles state off
} 
catch {
    Write-Host
    Write-Host "Something went wrong:" 
    Write-Host ($PSItem.Exception.Message)
    Write-Host

    # Sleep for 60 minutes so you can see the errors before the VM is destroyed by Packer.
    Start-Sleep -Seconds 3600

    Exit 1
}

Start-Sleep -Seconds 10