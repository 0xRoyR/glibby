using namespace System.Net
param($Request, $TriggerMetadata)
$resourceURI = “https://graph.microsoft.com/"
$tokenAuthURI = $env:IDENTITY_ENDPOINT + “?resource=$resourceURI&api-version=2019-08-01”
$tokenResponse = Invoke-RestMethod -Method Get -Headers @{ "X-IDENTITY-HEADER" = $env:IDENTITY_HEADER } -Uri $tokenAuthURI
Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode = [HttpStatusCode]::OK
    Body = $tokenResponse
})