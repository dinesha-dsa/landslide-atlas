param([Parameter(Mandatory=$true)][string]$ChapterPath,[Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$tourSynth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $tourSynth.SelectVoice('Microsoft Zira Desktop')
    $tourSynth.Rate = 0
    $tourFormat = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(24000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
    $tourChapters = Get-Content -LiteralPath $ChapterPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $tourIndex = 0
    foreach ($tourChapter in $tourChapters) {
        foreach ($tourSentence in $tourChapter.sentences) {
            $tourFile = Join-Path $OutputPath ('voice-{0:D2}.wav' -f $tourIndex)
            $tourSynth.SetOutputToWaveFile($tourFile, $tourFormat)
            $tourSynth.Speak([string]$tourSentence)
            $tourSynth.SetOutputToNull()
            $tourIndex++
        }
    }
} finally { $tourSynth.Dispose() }
