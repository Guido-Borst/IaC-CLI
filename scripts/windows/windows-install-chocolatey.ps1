# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<#
    .DESCRIPTION
    Installs dotnet framework 4.8, reboots, installs chocolatey
#>

param(
    [string] $BUILD_USERNAME = $env:BUILD_USERNAME
)

$ErrorActionPreference = "Continue"


# Install dotnet because Chocolatey otherwise fails --gbo
# Run a separate PowerShell process because the script calls exit, so it will end the current PowerShell session.
# We use a try-catch system because the first run it will install dotnet, which needs a reboot
try {
    Write-Output "Trying to install Chocolatey, could fail on first try"
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    choco feature enable -n allowGlobalConfirmation
    Get-EventLog -LogName * | ForEach { Clear-EventLog -LogName $_.Log }
}
catch {
    Write-Output "Rebooting, install Chocolatey again afterwards"
    shutdown /r /f /t 0 /c "packer restart"
    Write-Output "After reboot message"
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    choco feature enable -n allowGlobalConfirmation
    Get-EventLog -LogName * | ForEach { Clear-EventLog -LogName $_.Log }
}