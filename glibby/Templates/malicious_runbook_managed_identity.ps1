$tokenAuthURI = $env:MSI_ENDPOINT + "?resource=https://graph.microsoft.com/&api-version=2017-09-01"
$tokenResponse = Invoke-RestMethod -Method Get -Headers @{"Secret"="$env:MSI_SECRET"} -Uri $tokenAuthURI
$tokenResponse.access_token