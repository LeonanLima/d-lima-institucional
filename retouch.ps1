param(
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$OutputPath,
    [double]$MaxOpacity = 0.55,
    [double]$RegionStartPct = 0.42,
    [double]$FeatherPct = 0.12,
    [int]$BlurDownscale = 30
)

Add-Type -AssemblyName System.Drawing

$src = [System.Drawing.Image]::FromFile($InputPath)
$w = $src.Width
$h = $src.Height

# 1) Versao borrada via downscale -> upscale (box blur sem libs externas)
$smallW = [Math]::Max(1, [int]($w / $BlurDownscale))
$smallH = [Math]::Max(1, [int]($h / $BlurDownscale))

$small = New-Object System.Drawing.Bitmap $smallW, $smallH
$gSmall = [System.Drawing.Graphics]::FromImage($small)
$gSmall.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBilinear
$gSmall.DrawImage($src, 0, 0, $smallW, $smallH)
$gSmall.Dispose()

$blurred = New-Object System.Drawing.Bitmap $w, $h
$gBlur = [System.Drawing.Graphics]::FromImage($blurred)
$gBlur.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$gBlur.DrawImage($small, 0, 0, $w, $h)
$gBlur.Dispose()
$small.Dispose()

# 2) Resultado parte do original
$result = New-Object System.Drawing.Bitmap $w, $h
$gResult = [System.Drawing.Graphics]::FromImage($result)
$gResult.DrawImage($src, 0, 0, $w, $h)

# 3) Aplica o blur em bandas horizontais SO na regiao de baixo (pescoco/colo),
#    com opacidade crescendo gradualmente (feather) para nao deixar emenda visivel.
$regionStartY = [int]($h * $RegionStartPct)
$featherPx = [int]($h * $FeatherPct)
$bandHeight = 4

for ($y = $regionStartY; $y -lt $h; $y += $bandHeight) {
    $bh = [Math]::Min($bandHeight, $h - $y)
    $progress = ($y - $regionStartY) / [Math]::Max(1, $featherPx)
    if ($progress -gt 1) { $progress = 1 }
    $opacity = $MaxOpacity * $progress

    if ($opacity -le 0.01) { continue }

    $cm = New-Object System.Drawing.Imaging.ColorMatrix
    $cm.Matrix33 = $opacity
    $ia = New-Object System.Drawing.Imaging.ImageAttributes
    $ia.SetColorMatrix($cm, [System.Drawing.Imaging.ColorMatrixFlag]::Default, [System.Drawing.Imaging.ColorAdjustType]::Bitmap)

    $destRect = New-Object System.Drawing.Rectangle 0, $y, $w, $bh
    $gResult.DrawImage($blurred, $destRect, 0, $y, $w, $bh, [System.Drawing.GraphicsUnit]::Pixel, $ia)
}

$gResult.Dispose()
$blurred.Dispose()
$src.Dispose()

$jpegEncoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$encParams = New-Object System.Drawing.Imaging.EncoderParameters 1
$encParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 92
$result.Save($OutputPath, $jpegEncoder, $encParams)
$result.Dispose()

Write-Output "OK: $OutputPath"
