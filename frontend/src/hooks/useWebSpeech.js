// Simple Web Speech API hook (free, browser-based)
// Usage:
// const { start, stop, getTranscript, reset, isActive } = useWebSpeech()
// start(); ... stop(); const text = getTranscript(); reset();

export function useWebSpeech() {
  const state = {
    recognition: null,
    active: false,
    interim: '',
    final: '',
  }

  function start({ lang = 'en-US', continuous = true } = {}) {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) {
      throw new Error('Web Speech API not supported in this browser.')
    }
    const rec = new SR()
    rec.lang = lang
    rec.continuous = continuous
    rec.interimResults = true
    state.recognition = rec
    state.active = true

    rec.onresult = (e) => {
      let interim = ''
      let final = state.final
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const res = e.results[i]
        if (res.isFinal) final += res[0].transcript
        else interim += res[0].transcript
      }
      state.interim = interim
      state.final = final
      document.dispatchEvent(new CustomEvent('asr:update', { detail: { interim, final } }))
    }

    rec.onerror = () => { /* swallow or surface to UI */ }
    rec.onend = () => { state.active = false }

    rec.start()
  }

  function stop() {
    try { state.recognition?.stop() } catch {}
    state.active = false
  }

  function getTranscript() {
    return (state.final + ' ' + state.interim).trim()
  }

  function reset() {
    state.final = ''
    state.interim = ''
  }

  function isActive() { return state.active }

  return { start, stop, getTranscript, reset, isActive }
}
