#requires -Version 7.0
# Read-only API probe. Token and original response values are never printed.
$ErrorActionPreference = 'Stop'
$baseUrl = (Read-Host 'DocBee-URL (https://...)').Trim().TrimEnd('/') -replace '/restApi$', ''
$uri = [uri]$baseUrl
if ($uri.Scheme -ne 'https' -or -not $uri.Host -or $uri.UserInfo -or $uri.Query -or $uri.Fragment) {
    throw 'Bitte eine HTTPS-Instanz-URL ohne Zugangsdaten, Query oder Fragment eingeben.'
}
$token = Read-Host 'DocBee Access Token' -AsSecureString
$aliases = @{}

function Hide-DocBeeValues($value, [string]$field = '') {
    if ($null -eq $value) { return $null }
    if ($value -is [System.Collections.IDictionary]) {
        $result = [ordered]@{}
        foreach ($key in $value.Keys) {
            $result[$key] = Hide-DocBeeValues $value[$key] ([string]$key)
        }
        return $result
    }
    if ($value -is [pscustomobject]) {
        $result = [ordered]@{}
        foreach ($property in $value.PSObject.Properties) {
            $result[$property.Name] = Hide-DocBeeValues $property.Value $property.Name
        }
        return $result
    }
    if ($value -is [array]) {
        $items = @(foreach ($item in $value) { Hide-DocBeeValues $item $field })
        return ,$items
    }
    if ($field -in @('id', 'username')) {
        $key = "$field|$($value.GetType().Name)|$value"
        if (-not $aliases.ContainsKey($key)) {
            $aliases[$key] = "anonym-$($aliases.Count + 1)"
        }
        return $aliases[$key]
    }
    if ($value -is [bool]) { return $value }
    if ($field -in @('offset', 'limit', 'total', 'count', 'page', 'pages', 'totalCount', 'totalPages') -and $value -is [ValueType]) {
        return $value
    }
    return "<anonymisiert:$($value.GetType().Name)>"
}

try {
    foreach ($offset in @(0, 2)) {
        try {
            $response = Invoke-RestMethod -Method Get `
                -Uri "$baseUrl/restApi/v1/user?fields=id%2Cusername&limit=2&offset=$offset" `
                -Authentication Bearer -Token $token `
                -Headers @{ Accept = 'application/json' } `
                -MaximumRedirection 0 -TimeoutSec 30
            [ordered]@{
                requested_offset = $offset
                response = Hide-DocBeeValues $response
            } | ConvertTo-Json -Depth 30
        }
        catch {
            # Do not print the exception: it may contain server response data.
            $status = if ($null -ne $_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 'Verbindungsfehler' }
            Write-Output "Abfrage offset=$offset fehlgeschlagen: $status"
        }
    }
}
finally {
    $token.Dispose()
    Remove-Variable token, response -ErrorAction SilentlyContinue
    $aliases.Clear()
}
