# PowerShell script to add firewall rule for Python Reminder App
# This script requires Administrator privileges

Write-Host "Adding Windows Firewall rule for Python Reminder App..." -ForegroundColor Yellow

try {
    # Add inbound rule for port 8001
    New-NetFirewallRule `
        -DisplayName "Python Reminder App Port 8001" `
        -Direction Inbound `
        -LocalPort 8001 `
        -Protocol TCP `
        -Action Allow `
        -Profile Any `
        -ErrorAction Stop
    
    Write-Host "✅ Firewall rule added successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now access the app from your iPhone at:" -ForegroundColor Cyan
    Write-Host "http://192.168.0.106:8001" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
catch {
    Write-Host "❌ Error adding firewall rule: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "This script must be run as Administrator." -ForegroundColor Yellow
    Write-Host "Please right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
