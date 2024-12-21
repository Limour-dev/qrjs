$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://+:80/")
$listener.Start()
Write-Host "Listening..."

while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response
    $response.Headers.Add("Content-Type", "application/octet-stream")

    $file = "$(Get-Location)\client.html"
    $buffer = [System.IO.File]::ReadAllBytes($file)
    $response.ContentLength64 = $buffer.Length
    $output = $response.OutputStream
    $output.Write($buffer, 0, $buffer.Length)
    $output.Close()
}