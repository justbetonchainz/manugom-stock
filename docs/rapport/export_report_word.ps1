$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$docxPath = Join-Path $projectRoot 'output\docx\Rapport_MANUGOM_Stock.docx'
$pdfPath = Join-Path $projectRoot 'output\pdf\Rapport_MANUGOM_Stock.pdf'

if (-not (Test-Path -LiteralPath $docxPath)) {
    throw "Document Word introuvable : $docxPath"
}

$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($docxPath, $false, $false)
    $document.TrackRevisions = $false
    $document.Repaginate()

    foreach ($toc in $document.TablesOfContents) {
        $toc.Update()
    }
    foreach ($tableOfFigures in $document.TablesOfFigures) {
        $tableOfFigures.Update()
    }
    foreach ($field in $document.Fields) {
        $null = $field.Update()
    }

    $document.Repaginate()
    foreach ($toc in $document.TablesOfContents) {
        $toc.UpdatePageNumbers()
    }
    foreach ($tableOfFigures in $document.TablesOfFigures) {
        $tableOfFigures.UpdatePageNumbers()
    }

    $document.Save()
    $document.ExportAsFixedFormat($pdfPath, 17)
    Write-Output "DOCX mis à jour : $docxPath"
    Write-Output "PDF exporté : $pdfPath"
    Write-Output "Pages Word : $($document.ComputeStatistics(2))"
}
finally {
    if ($document -ne $null) {
        $document.Close($false)
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($document) | Out-Null
    }
    if ($word -ne $null) {
        $word.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
