---
name: ace-music
description: Generate AI music using ACE-Step 1.5 via ACE Music's free API. Use when the user asks to create, generate, or compose music, songs, beats, instrumentals, or audio tracks. Supports lyrics, style prompts, covers, and repainting. Free API, no cost.
---

# ACE Music - AI Music Generation

Generate music with model generated lyrics and provided style prompts.

## Setup

**API Key** is stored in env `ACE_MUSIC_API_KEY`. If not set:
1. Open https://acemusic.ai/playground/api-key in the browser for the user
2. Ask them to sign up (free) and paste the API key
3. Store it: `export ACE_MUSIC_API_KEY=<key>`

## Tools available
- `generate_music` - Main tool to generate music based on prompts and parameters

## Tools Usage

### Simple generation
files = generate_music(
    prompt="upbeat pop song about summer",
    duration=30
)

Returns: ['/absolute/path/to/output_<timestamp>.mp3']

### With lyrics
files = generate_music(
    prompt="pop song",
    lyrics="Hello world, this is my song",
    output="my_song.mp3"
)

### Instrumental with BPM and key
files = generate_music(
    prompt="calm piano melody",
    instrumental=True,
    bpm=80,
    key_scale="C major",
    duration=45,
    output="piano.mp3"
)

### Batch generation (3 variations)
files = generate_music(
    prompt="rock song",
    batch_size=3,
    output="rock.mp3"
)

Returns: ['/path/to/rock_1.mp3', '/path/to/rock_2.mp3', '/path/to/rock_3.mp3']

### Sample mode (explore random)
files = generate_music(
    sample_mode=True,
    output="sample.mp3"
)


**Parameters:**
- `prompt`: Music description
- `lyrics`: Song lyrics (optional)
- `duration`: Duration in seconds
- `language`: Vocal language (default: "en")
- `instrumental`: Generate instrumental (default: False)
- `output`: Output file path (default: auto-generated timestamp name)
- `bpm`: Beats per minute
- `key_scale`: Musical key/scale (e.g., "C major")
- `seed`: Random seed for reproducibility
- `sample_mode`: Enable sample mode (default: False)
- `batch_size`: Number of variations (default: 1)
- `output_format`: Audio format (default: "mp3")
- `api_key`: API key (optional, uses env var ACE_MUSIC_API_KEY)
- `base_url`: API URL (optional, default: https://api.acemusic.ai)

**Returns:** List of absolute file paths to generated audio files

## Instructions
1. Based on use provided theme, mood, or style, call `generate_music` with appropriate parameters
2. Specify the output file location in workspace folder
3. Handle any errors gracefully (e.g., API errors, missing parameters) and provide helpful feedback to the user