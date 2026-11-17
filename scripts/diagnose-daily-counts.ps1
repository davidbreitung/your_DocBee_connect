# Read-only diagnosis for Windows PowerShell 5.1 / PowerShell 7.
# Review error messages before sharing: DocBee may include instance-specific data.
param([uri]$BaseUrl = 'https://my.docbee.com')
$ErrorActionPreference = 'Stop'
if ($BaseUrl.Scheme -ne 'https' -or $BaseUrl.UserInfo -or $BaseUrl.Query -or $BaseUrl.Fragment) {
    throw 'Use an HTTPS instance URL without credentials, query or fragment.'
}
$secureToken = Read-Host 'DocBee Bearer-Token' -AsSecureString
$credential = [System.Net.NetworkCredential]::new('', $secureToken)
try {
    $headers = @{ Authorization = 'Bearer ' + $credential.Password }
    # Local Windows midnight: diagnostic only, HA still uses its own timezone.
    $start = (Get-Date).Date.ToUniversalTime()
    $end = (Get-Date).ToUniversalTime()
    $tests = @(
        @{ Name = 'baseline'; Scope = $null; DateFormat = $null; Sort = $true },
        @{ Name = 'modified-offset'; Scope = 'TICKET_MODIFIED'; DateFormat = "yyyy-MM-dd'T'HH:mm:ss.ffffff'+00:00'"; Sort = $true },
        @{ Name = 'modified-Z'; Scope = 'TICKET_MODIFIED'; DateFormat = "yyyy-MM-dd'T'HH:mm:ss.fff'Z'"; Sort = $true },
        @{ Name = 'modified-Z-without-sort'; Scope = 'TICKET_MODIFIED'; DateFormat = "yyyy-MM-dd'T'HH:mm:ss.fff'Z'"; Sort = $false },
        @{ Name = 'created-Z'; Scope = 'TICKET_CREATED'; DateFormat = "yyyy-MM-dd'T'HH:mm:ss.fff'Z'"; Sort = $true },
        @{ Name = 'closed-Z'; Scope = 'TICKET_CLOSED'; DateFormat = "yyyy-MM-dd'T'HH:mm:ss.fff'Z'"; Sort = $true }
    )
    $results = foreach ($test in $tests) {
        $params = [ordered]@{ fields = 'id'; limit = '1'; offset = '0' }
        if ($test.Sort) { $params.sortings = 'id asc' }
        if ($test.Scope) {
            $params.ticketScope = $test.Scope
            $params.startDate = $start.ToString($test.DateFormat, [Globalization.CultureInfo]::InvariantCulture)
            $params.endDate = $end.ToString($test.DateFormat, [Globalization.CultureInfo]::InvariantCulture)
        }
        $query = ($params.GetEnumerator() | ForEach-Object {
            [uri]::EscapeDataString($_.Key) + '=' + [uri]::EscapeDataString([string]$_.Value)
        }) -join '&'
        $url = $BaseUrl.AbsoluteUri.TrimEnd('/') + '/restApi/v1/ticket?' + $query
        try {
            $null = Invoke-RestMethod -Uri $url -Headers $headers -Method Get -MaximumRedirection 0 -TimeoutSec 30
            [pscustomobject]@{ Test = $test.Name; Status = 200; Error = $null }
        }
        catch {
            $status = $null
            if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode }
            $message = $_.ErrorDetails.Message
            if (-not $message) { $message = 'No response error details available' }
            if ($message.Length -gt 2000) { $message = $message.Substring(0, 2000) }
            [pscustomobject]@{ Test = $test.Name; Status = $status; Error = $message }
        }
    }
    $results | ConvertTo-Json -Depth 4
}
finally {
    Remove-Variable secureToken, credential, headers -ErrorAction SilentlyContinue
}
