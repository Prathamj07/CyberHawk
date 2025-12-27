import os
import re
import tempfile
import subprocess
import requests
from typing import Optional, Dict, Callable
from bs4 import BeautifulSoup
from elevenlabs import ElevenLabs, VoiceSettings
from google import genai


class ArticleToPodcast:
    """Handles conversion of articles or URLs to multi-speaker podcast audio"""

    def __init__(self, gemini_api_key: str, elevenlabs_api_key: str):
        """Initialize article to podcast service with Gemini and ElevenLabs APIs"""
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

        # Voice mapping for different speakers
        self.host_voice_id = "pNInz6obpgDQGcFmaJgB"    # Adam - Host voice
        self.expert_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - Expert voice

    # ------------------ NEW: Article Fetching Logic ------------------ #
    def fetch_article_from_url(self, url: str) -> Optional[str]:
        """Fetches and extracts article text from a given URL"""
        print(f"🔍 Fetching article from: {url}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/118.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to fetch article: {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else "Untitled"

            # Extract paragraphs
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
            if not paragraphs:
                print("⚠️ No paragraph content found.")
                return None

            article_text = f"{title_text}\n\n" + " ".join(paragraphs[:8])
            return article_text.strip()

        except Exception as e:
            print(f"Error fetching article: {e}")
            return None

    # ---------------------------------------------------------------- #

    def _is_url(self, text: str) -> bool:
        """Check if input is a valid URL"""
        return bool(re.match(r'https?://', text.strip()))

    def generate_podcast_script(self, article_text: str, word_count: int = 300) -> Optional[str]:
        """Generate a podcast script from article text using Gemini"""
        try:
            prompt = f"""
Summarize the following article into a detailed podcast script (~{word_count} words) as a conversation:
- Include "Host:" and "Expert:" labels.
- Host introduces topic and asks questions.
- Expert explains with depth and insights.
- Keep it engaging and natural.

Article:
---
{article_text}
---
"""
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            if response and response.text:
                return response.text.strip()
            else:
                return self._generate_fallback_script(article_text)

        except Exception as e:
            print(f"Error generating podcast script: {e}")
            return self._generate_fallback_script(article_text)

    def _generate_fallback_script(self, article_text: str) -> str:
        """Generate a simple fallback script if AI generation fails"""
        words = article_text.split()[:100]
        summary = ' '.join(words)
        return f"""Host: Welcome to our podcast. Today, we're discussing an interesting article.
Expert: {summary}
Host: That's fascinating. Can you explain more?
Expert: Sure! This article highlights some key insights worth discussing.
Host: Thanks for sharing these thoughts.
Expert: My pleasure!"""

    def generate_speaker_audio(self, text: str, voice_id: str, output_file: str) -> bool:
        """Generate audio for one speaker line using ElevenLabs"""
        try:
            audio_generator = self.elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
                voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
            )
            with open(output_file, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Error generating audio: {e}")
            return False

    def merge_audio_files(self, audio_files: list, output_file: str) -> bool:
        """Merge multiple audio files into one using FFmpeg"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file}'\n")
                file_list_path = f.name

            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", file_list_path, "-c", "copy", output_file
            ], check=True, capture_output=True)

            os.unlink(file_list_path)
            return True
        except Exception as e:
            print(f"Error merging audio: {e}")
            return False

    def create_podcast_from_article(self, input_text: str,
                                    script_word_count: int = 300,
                                    progress_callback: Optional[Callable] = None) -> Optional[bytes]:
        """
        Complete workflow to convert text or URL to podcast audio.
        - Detects if input is a URL and fetches the article if so.
        - Generates script, voiceovers, and merges final audio.
        """
        try:
            # Step 0: Detect URL and fetch article text
            if self._is_url(input_text):
                if progress_callback:
                    progress_callback("Fetching article content from URL...", 10)
                article_text = self.fetch_article_from_url(input_text)
                if not article_text:
                    if progress_callback:
                        progress_callback("Failed to fetch article from URL.", 100)
                    return None
            else:
                article_text = input_text

            # Step 1: Generate podcast script
            if progress_callback:
                progress_callback("Generating podcast script...", 25)
            script = self.generate_podcast_script(article_text, script_word_count)
            if not script:
                return None

            # Step 2: Generate audio segments
            if progress_callback:
                progress_callback("Generating audio for speakers...", 50)
            lines = script.strip().split('\n')
            audio_files = []
            temp_files = []

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                if line.lower().startswith("host:"):
                    voice_id = self.host_voice_id
                    text = line[5:].strip()
                elif line.lower().startswith("expert:"):
                    voice_id = self.expert_voice_id
                    text = line[7:].strip()
                else:
                    continue

                temp_audio = tempfile.mktemp(suffix=f'_speaker_{i}.mp3')
                temp_files.append(temp_audio)
                if self.generate_speaker_audio(text, voice_id, temp_audio):
                    audio_files.append(temp_audio)

                if progress_callback:
                    progress = 50 + int((i / len(lines)) * 35)
                    progress_callback(f"Processing line {i+1}/{len(lines)}...", progress)

            if not audio_files:
                return None

            # Step 3: Merge audio files
            if progress_callback:
                progress_callback("Merging audio segments...", 90)
            final_output = tempfile.mktemp(suffix='_podcast.mp3')
            temp_files.append(final_output)
            if not self.merge_audio_files(audio_files, final_output):
                return None

            # Step 4: Read final output
            with open(final_output, 'rb') as f:
                audio_bytes = f.read()

            # Clean temp files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass

            if progress_callback:
                progress_callback("✅ Podcast creation complete!", 100)

            return audio_bytes

        except Exception as e:
            print(f"Error creating podcast: {e}")
            return None
