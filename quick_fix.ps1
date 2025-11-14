# Cyber Essentials 2025 - Quick Remediation Script
# Run as Administrator

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Cyber Essentials 2025 - Quick Fixes" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Function to display section headers
function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "--------------------------------------------" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "--------------------------------------------" -ForegroundColor Cyan
}

# 1. Check and configure screen lock timeout
Write-Section "1. Configuring Screen Lock Timeout"

try {
    # Set screen saver timeout to 15 minutes (900 seconds)
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "ScreenSaveTimeOut" -Value "900" -Type String
    Write-Host "[OK] Screen saver timeout set to 15 minutes" -ForegroundColor Green
    
    # Enable screen saver password protection
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "ScreenSaverIsSecure" -Value "1" -Type String
    Write-Host "[OK] Screen saver password protection enabled" -ForegroundColor Green
    
    # Set screen timeout via power settings (15 minutes = 900 seconds)
    powercfg /change monitor-timeout-ac 15
    powercfg /change monitor-timeout-dc 10
    Write-Host "[OK] Display timeout configured" -ForegroundColor Green
}
catch {
    Write-Host "[WARN] Could not configure all screen lock settings: $_" -ForegroundColor Yellow
}

# 2. Check Windows Hello status
Write-Section "2. Checking Windows Hello / MFA Status"

try {
    $helloConfigs = Get-Item 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Hello\Configs\*' -ErrorAction SilentlyContinue
    if ($helloConfigs) {
        Write-Host "[OK] Windows Hello is configured" -ForegroundColor Green
    }
    else {
        Write-Host "[WARN] Windows Hello not detected" -ForegroundColor Yellow
        Write-Host "       ACTION REQUIRED: Configure Windows Hello PIN" -ForegroundColor Yellow
        Write-Host "       Go to: Settings → Accounts → Sign-in options → PIN" -ForegroundColor White
    }
}
catch {
    Write-Host "[WARN] Cannot determine Windows Hello status" -ForegroundColor Yellow
}

# Check for biometric devices
$biometricDevices = Get-PnpDevice -Class Biometric -Status OK -ErrorAction SilentlyContinue
if ($biometricDevices) {
    Write-Host "[OK] Biometric device(s) available: $($biometricDevices.Count)" -ForegroundColor Green
}

# 3. Check BitLocker status
Write-Section "3. Checking BitLocker Encryption Status"

try {
    $volumes = Get-BitLockerVolume -ErrorAction Stop
    foreach ($vol in $volumes) {
        $status = $vol.VolumeStatus
        $mount = $vol.MountPoint
        
        if ($status -eq "FullyEncrypted") {
            Write-Host "[OK] $mount - Fully Encrypted" -ForegroundColor Green
        }
        elseif ($status -eq "EncryptionInProgress") {
            Write-Host "[INFO] $mount - Encryption in progress..." -ForegroundColor Cyan
        }
        else {
            Write-Host "[FAIL] $mount - NOT ENCRYPTED (Status: $status)" -ForegroundColor Red
            Write-Host "       ACTION REQUIRED: Enable BitLocker" -ForegroundColor Yellow
            Write-Host "       Command: Enable-BitLocker -MountPoint '$mount' -EncryptionMethod XtsAes256 -RecoveryPasswordProtector" -ForegroundColor White
        }
    }
}
catch {
    Write-Host "[WARN] Cannot check BitLocker status: $_" -ForegroundColor Yellow
    Write-Host "       This device may not support BitLocker" -ForegroundColor Yellow
}

# 4. Check Windows version and support status
Write-Section "4. Checking Windows Version Support"

$version = [System.Environment]::OSVersion.Version
$productName = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").ProductName

Write-Host "OS: $productName" -ForegroundColor White
Write-Host "Version: $($version.Major).$($version.Minor).$($version.Build)" -ForegroundColor White

if ($productName -like "*Windows 11*") {
    Write-Host "[OK] Windows 11 is supported until October 2031" -ForegroundColor Green
}
elseif ($productName -like "*Windows 10*") {
    Write-Host "[FAIL] Windows 10 reached End-of-Life on October 14, 2025" -ForegroundColor Red
    Write-Host "       ACTION REQUIRED: Upgrade to Windows 11 immediately" -ForegroundColor Yellow
    Write-Host "       This is MANDATORY for Cyber Essentials 2025 certification" -ForegroundColor Yellow
}
else {
    Write-Host "[WARN] Unknown Windows version" -ForegroundColor Yellow
}

# 5. Check recent updates
Write-Section "5. Checking Windows Update Status"

try {
    $hotfixes = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1
    if ($hotfixes -and $hotfixes.InstalledOn) {
        $daysSince = (Get-Date) - $hotfixes.InstalledOn
        Write-Host "Last update: $($hotfixes.InstalledOn.ToString('yyyy-MM-dd')) ($([int]$daysSince.TotalDays) days ago)" -ForegroundColor White
        
        if ($daysSince.TotalDays -le 14) {
            Write-Host "[OK] Updates are current (within 14-day requirement)" -ForegroundColor Green
        }
        elseif ($daysSince.TotalDays -le 30) {
            Write-Host "[WARN] Updates are older than 14 days" -ForegroundColor Yellow
            Write-Host "       ACTION REQUIRED: Run Windows Update" -ForegroundColor Yellow
        }
        else {
            Write-Host "[FAIL] Updates are older than 30 days" -ForegroundColor Red
            Write-Host "       ACTION REQUIRED: Run Windows Update immediately" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "[WARN] Cannot determine last update date" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[WARN] Cannot check update status: $_" -ForegroundColor Yellow
}

# 6. Check Azure AD join status
Write-Section "6. Checking Azure AD / MDM Status"

try {
    $dsregcmd = dsregcmd /status
    $azureAdJoined = $dsregcmd | Select-String "AzureAdJoined"
    
    if ($azureAdJoined -like "*YES*") {
        Write-Host "[OK] Device is joined to Azure AD" -ForegroundColor Green
    }
    else {
        Write-Host "[WARN] Device is NOT joined to Azure AD" -ForegroundColor Yellow
        Write-Host "       RECOMMENDED: Join to Azure AD for centralized management" -ForegroundColor Yellow
        Write-Host "       Go to: Settings → Accounts → Access work or school" -ForegroundColor White
    }
}
catch {
    Write-Host "[WARN] Cannot check Azure AD status" -ForegroundColor Yellow
}

# 7. Check default accounts
Write-Section "7. Checking Default Accounts"

$defaultAccounts = @("Guest", "Administrator", "DefaultAccount")

foreach ($account in $defaultAccounts) {
    try {
        $user = net user $account 2>$null
        if ($user -match "Account active\s+Yes") {
            Write-Host "[WARN] $account account is ENABLED" -ForegroundColor Yellow
            Write-Host "       RECOMMENDED: Disable with: net user $account /active:no" -ForegroundColor White
        }
        elseif ($user -match "Account active\s+No") {
            Write-Host "[OK] $account account is disabled" -ForegroundColor Green
        }
    }
    catch {
        # Account might not exist
    }
}

# 8. Check VPN configuration
Write-Section "8. Checking VPN Configuration"

try {
    $vpnConnections = Get-VpnConnection -AllUserConnection -ErrorAction SilentlyContinue
    if ($vpnConnections) {
        Write-Host "[OK] VPN connection(s) configured: $($vpnConnections.Count)" -ForegroundColor Green
        foreach ($vpn in $vpnConnections) {
            Write-Host "     - $($vpn.Name)" -ForegroundColor White
        }
    }
    else {
        Write-Host "[WARN] No VPN connections found" -ForegroundColor Yellow
        Write-Host "       REQUIRED for remote work: Configure VPN" -ForegroundColor Yellow
        Write-Host "       Go to: Settings → Network & Internet → VPN" -ForegroundColor White
    }
}
catch {
    Write-Host "[WARN] Cannot check VPN status" -ForegroundColor Yellow
}

# 9. Summary
Write-Section "Summary & Next Steps"

Write-Host ""
Write-Host "Quick fixes applied:" -ForegroundColor Cyan
Write-Host "  ✓ Screen lock timeout set to 15 minutes" -ForegroundColor Green
Write-Host "  ✓ Screen saver password protection enabled" -ForegroundColor Green
Write-Host ""
Write-Host "Manual actions required:" -ForegroundColor Yellow
Write-Host "  1. Enable Windows Hello PIN (if not already configured)" -ForegroundColor White
Write-Host "  2. Enable BitLocker on all drives (if not encrypted)" -ForegroundColor White
Write-Host "  3. Upgrade to Windows 11 (if running Windows 10)" -ForegroundColor White
Write-Host "  4. Run Windows Update (if updates > 14 days old)" -ForegroundColor White
Write-Host "  5. Join Azure AD (for MDM enrollment)" -ForegroundColor White
Write-Host "  6. Configure VPN (for remote work)" -ForegroundColor White
Write-Host ""
Write-Host "Re-run the scanner to verify changes:" -ForegroundColor Cyan
Write-Host "  python -m scanner.main --output report.json" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
