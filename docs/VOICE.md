# HAKHAM Infinity Voice

## Voice architecture

HAKHAM keeps reasoning and voice separated:

```text
Ach microphone
    -> browser speech recognition (v0.1)
    -> HAKHAM Core
    -> configured reasoning engine (for example GPT-6 Astra via Abacus)
    -> text response
    -> OpenAI natural TTS when configured
    -> browser audio playback
```

If OpenAI TTS is not configured or a speech request fails, the Control Center falls back to the browser/OS speech synthesizer.

## Natural GPT voice

Configure only in the local `.env`:

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE=cedar
OPENAI_TTS_SPEED=1.05
OPENAI_TTS_INSTRUCTIONS=
```

The browser never receives `OPENAI_API_KEY`. It calls the HAKHAM backend at `/api/voice/speech`, and the backend calls OpenAI.

The default voice direction asks for Brazilian Portuguese, a mature and confident conversational delivery, short natural pauses, and no announcer-style reading. `OPENAI_TTS_INSTRUCTIONS` can override that direction.

## Control Center behavior

The v0.4 Control Center exposes two speech engines:

- `GPT Natural`: OpenAI speech generation through the HAKHAM backend.
- `Browser`: free fallback using the browser/operating-system synthesizer.

The selected speech engine is stored only as a browser preference. If GPT Natural is unavailable, HAKHAM automatically uses Browser voice.

## Current scope

- Speech-to-text is still browser-native in v0.4.
- Text-to-speech can use OpenAI natural speech.
- The reasoning engine remains independent from the voice engine.
- Realtime duplex audio, interruption/barge-in, and a permanent custom HAKHAM voice are later milestones.
