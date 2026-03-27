#!/usr/bin/env python3
"""
ACE-Step Music Generation via API

Generate music using the ACE Music API with support for lyrics, duration,
language, instrumental mode, BPM, key/scale, seed, sample mode, and batch generation.

Usage:
    python generate_music.py <prompt> [options]
    
Example:
    python generate_music.py "upbeat pop song" --duration 30 --lyrics "Hello world"
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


class ACEMusicGenerator:
    """ACE Music API client for generating music."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize the ACE Music generator.
        
        Args:
            api_key: ACE Music API key (defaults to ACE_MUSIC_API_KEY env var)
            base_url: API base URL (defaults to ACE_MUSIC_BASE_URL env var or https://api.acemusic.ai)
        """
        self.api_key = api_key or os.getenv("ACE_MUSIC_API_KEY", "")
        self.base_url = base_url or os.getenv("ACE_MUSIC_BASE_URL", "https://api.acemusic.ai")
        
        if not self.api_key:
            raise ValueError(
                "ACE_MUSIC_API_KEY not set. "
                "Get your free API key at: https://acemusic.ai/playground/api-key"
            )
    
    def generate(
        self,
        prompt: Optional[str] = None,
        lyrics: Optional[str] = None,
        duration: Optional[int] = None,
        language: str = "en",
        instrumental: Optional[bool] = None,
        bpm: Optional[int] = None,
        key_scale: Optional[str] = None,
        seed: Optional[int] = None,
        sample_mode: bool = False,
        batch_size: int = 1,
        output_format: str = "mp3"
    ) -> Dict[str, Any]:
        """
        Generate music using the ACE Music API.
        
        Args:
            prompt: Description of the music to generate
            lyrics: Lyrics for the song (optional)
            duration: Duration in seconds
            language: Vocal language code (default: "en")
            instrumental: Whether to generate instrumental music
            bpm: Beats per minute
            key_scale: Musical key/scale (e.g., "C major")
            seed: Random seed for reproducibility
            sample_mode: Enable sample mode
            batch_size: Number of variations to generate
            output_format: Audio format (default: "mp3")
            
        Returns:
            Dictionary with response data and audio information
        """
        # Build audio config
        audio_config = {
            "vocal_language": language,
            "format": output_format
        }
        
        if duration is not None:
            audio_config["duration"] = duration
        if bpm is not None:
            audio_config["bpm"] = bpm
        if instrumental is not None:
            audio_config["instrumental"] = instrumental
        if key_scale is not None:
            audio_config["key_scale"] = key_scale
        
        # Build message content
        if lyrics and prompt:
            # Tagged mode: both prompt and lyrics
            content = f"<prompt>{prompt}</prompt>\n<lyrics>{lyrics}</lyrics>"
        elif lyrics:
            content = lyrics
        elif prompt:
            content = prompt
        elif not sample_mode:
            raise ValueError("Either 'prompt' or 'lyrics' must be provided, or enable sample_mode")
        else:
            content = ""  # sample_mode allows empty content
        
        # Build request body
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "audio_config": audio_config,
            "stream": False
        }
        
        if sample_mode:
            body["sample_mode"] = True
        if seed is not None:
            body["seed"] = seed
        if batch_size > 1:
            body["batch_size"] = batch_size
        
        # Log generation info
        print(f"🎵 Generating music...", file=sys.stderr)
        print(f"   Prompt: {prompt or '[lyrics/sample mode]'}", file=sys.stderr)
        if duration:
            print(f"   Duration: {duration}s", file=sys.stderr)
        print(f"   Language: {language}", file=sys.stderr)
        
        # Make API request
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"ERROR: API request failed: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print(e.response.text, file=sys.stderr)
                except:
                    pass
            raise
        
        # Validate response
        if "choices" not in data:
            print("ERROR: Invalid API response format", file=sys.stderr)
            print(json.dumps(data, indent=2), file=sys.stderr)
            raise ValueError("Invalid API response: missing 'choices' field")
        
        return data
    
    def save_audio(
        self,
        response_data: Dict[str, Any],
        output_path: str = None
    ) -> List[str]:
        """
        Extract and save audio files from API response.
        
        Args:
            response_data: Response dictionary from generate()
            output_path: Base path for output file(s) (defaults to output_<timestamp>.mp3)
            
        Returns:
            List of saved file paths
        """
        if output_path is None:
            output_path = f"output_{int(time.time())}.mp3"
        
        # Extract message
        try:
            message = response_data["choices"][0]["message"]
            audios = message.get("audio", [])
            metadata = message.get("content", "")
        except (KeyError, IndexError) as e:
            print(f"ERROR: Failed to extract audio from response: {e}", file=sys.stderr)
            raise ValueError("Invalid response structure")
        
        if not audios:
            print("ERROR: No audio in response", file=sys.stderr)
            print(json.dumps(response_data, indent=2), file=sys.stderr)
            raise ValueError("No audio data in response")
        
        # Save audio file(s)
        saved_files = []
        output_parts = Path(output_path).stem, Path(output_path).suffix
        
        for i, audio_item in enumerate(audios):
            try:
                audio_url = audio_item["audio_url"]["url"]
                
                # Extract base64 data (format: data:audio/mpeg;base64,<data>)
                if "," in audio_url:
                    b64_data = audio_url.split(",", 1)[1]
                else:
                    b64_data = audio_url
                
                # Decode and save
                audio_bytes = base64.b64decode(b64_data)
                
                if len(audios) == 1:
                    filename = output_path
                else:
                    filename = f"{output_parts[0]}_{i+1}{output_parts[1]}"
                
                with open(filename, "wb") as f:
                    f.write(audio_bytes)
                
                print(f"Saved: {filename}", file=sys.stderr)
                saved_files.append(filename)
                
            except (KeyError, IndexError, base64.binascii.Error) as e:
                print(f"ERROR: Failed to decode audio {i+1}: {e}", file=sys.stderr)
                continue
        
        # Print metadata if available
        if metadata:
            print("", file=sys.stderr)
            print("📋 Metadata:", file=sys.stderr)
            print(metadata, file=sys.stderr)
        
        return saved_files


def generate_music(
    prompt: Optional[str] = None,
    lyrics: Optional[str] = None,
    duration: Optional[int] = None,
    language: str = "en",
    instrumental: bool = False,
    output: Optional[str] = None,
    bpm: Optional[int] = None,
    key_scale: Optional[str] = None,
    seed: Optional[int] = None,
    sample_mode: bool = False,
    batch_size: int = 1,
    output_format: str = "mp3",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None
) -> List[str]:
    """
    Generate music and return saved file path(s).
    
    Args:
        prompt: Description of the music to generate
        lyrics: Lyrics for the song (optional)
        duration: Duration in seconds
        language: Vocal language code (default: "en")
        instrumental: Whether to generate instrumental music (default: False)
        output: Output file path (default: output_<timestamp>.mp3)
        bpm: Beats per minute
        key_scale: Musical key/scale (e.g., "C major")
        seed: Random seed for reproducibility
        sample_mode: Enable sample mode (default: False)
        batch_size: Number of variations to generate (default: 1)
        output_format: Audio format (default: "mp3")
        api_key: ACE Music API key (defaults to ACE_MUSIC_API_KEY env var)
        base_url: API base URL (defaults to ACE_MUSIC_BASE_URL env var)
        
    Returns:
        List of saved file paths (absolute paths)
    """
    # Initialize generator
    generator = ACEMusicGenerator(api_key=api_key, base_url=base_url)
    
    # Generate music
    response_data = generator.generate(
        prompt=prompt,
        lyrics=lyrics,
        duration=duration,
        language=language,
        instrumental=instrumental if instrumental else None,
        bpm=bpm,
        key_scale=key_scale,
        seed=seed,
        sample_mode=sample_mode,
        batch_size=batch_size,
        output_format=output_format
    )
    
    # Save audio files and get paths
    saved_files = generator.save_audio(response_data, output)
    
    # Convert to absolute paths
    absolute_paths = [str(Path(f).resolve()) for f in saved_files]
    
    return absolute_paths


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate music using ACE Music API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from prompt
  %(prog)s "upbeat pop song about summer"
  
  # With lyrics
  %(prog)s "pop song" --lyrics "Hello world, this is my song"
  
  # Instrumental with specific BPM and key
  %(prog)s "calm piano melody" --instrumental --bpm 80 --key "C major" --duration 45
  
  # Batch generation
  %(prog)s "rock song" --batch 3 --output rock_variations.mp3
  
  # Sample mode (explore random samples)
  %(prog)s --sample-mode --output sample.mp3
        """
    )
    
    parser.add_argument("prompt", nargs="?", help="Music description prompt")
    parser.add_argument("--lyrics", help="Song lyrics")
    parser.add_argument("--duration", type=int, help="Duration in seconds (e.g., 30)")
    parser.add_argument("--language", default="en", help="Vocal language code (default: en)")
    parser.add_argument("--instrumental", action="store_true", help="Generate instrumental music")
    parser.add_argument("-o", "--output", help="Output file path (default: output_<timestamp>.mp3)")
    parser.add_argument("--bpm", type=int, help="Beats per minute")
    parser.add_argument("--key", dest="key_scale", help="Musical key/scale (e.g., 'C major')")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--sample-mode", action="store_true", help="Enable sample mode")
    parser.add_argument("--batch", type=int, default=1, dest="batch_size", 
                        help="Number of variations to generate (default: 1)")
    parser.add_argument("--format", default="mp3", dest="output_format",
                        help="Audio format (default: mp3)")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.prompt and not args.sample_mode and not args.lyrics:
        parser.error("Either 'prompt', '--lyrics', or '--sample-mode' must be provided")
    
    try:
        # Generate music
        saved_files = generate_music(
            prompt=args.prompt,
            lyrics=args.lyrics,
            duration=args.duration,
            language=args.language,
            instrumental=args.instrumental,
            output=args.output,
            bpm=args.bpm,
            key_scale=args.key_scale,
            seed=args.seed,
            sample_mode=args.sample_mode,
            batch_size=args.batch_size,
            output_format=args.output_format
        )
        
        # Print saved file paths (for script chaining)
        for filename in saved_files:
            print(filename)
        
        return 0
        
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
