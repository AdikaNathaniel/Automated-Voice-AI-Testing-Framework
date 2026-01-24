Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile("c:\automated-voice-testing-e\automated-voice-testing-e\test_audio\play_music.wav")
$synth.Speak("Hey assistant, play some music")
$synth.Dispose()
Write-Host "Audio file created: play_music.wav"
