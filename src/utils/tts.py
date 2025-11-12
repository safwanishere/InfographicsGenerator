import json
import os
import uuid
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict

import edge_tts


class EdgeTTSNarrationGenerator:
    """Generates crystal-clear audio narrations using Microsoft Edge TTS"""
    
    # Best quality voices for narration
    VOICES = {
        'male_professional': 'en-US-GuyNeural',
        'female_professional': 'en-US-JennyNeural',
        'male_narrator': 'en-US-EricNeural',
        'female_narrator': 'en-US-AriaNeural',
    }
    
    def __init__(self, 
                 output_base_dir: str = "src/static/outputs/audio",
                 voice: str = 'male_narrator'):
        """
        Initialize the Edge TTS audio generator
        """
        self.output_dir = Path(output_base_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.voice = self.VOICES.get(voice, self.VOICES['male_narrator'])
        print(f"Using voice: {self.voice}")
    
    def load_narration_json(self, json_path: str) -> List[Dict]:
        """Load narration data from JSON file"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('result', [])
        except FileNotFoundError:
            print(f"Error: Could not find '{json_path}'")
            print("Please ensure the narrationOutput.json file exists.")
            return []
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{json_path}'")
            return []
    
    def clean_text_for_tts(self, text: str) -> str:
        """Clean and optimize text for better TTS pronunciation"""
        text = text.replace('\n', '. ')
        text = text.replace('  ', ' ')
        
        # Improve pronunciation of common technical terms
        replacements = {
            'ANSI/NECA': 'ANSI NECA', 'LED': 'L.E.D.', 'MUTCD': 'M.U.T.C.D.',
            'NIST': 'N.I.S.T.', 'sq. yd': 'square yard', 'sq. m': 'square meter',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()
    
    async def generate_audio_async(self,
                                   text: str,
                                   chunk_index: int,
                                   section: str = "",
                                   title: str = "") -> str:
        """
        Generate a single audio file asynchronously.
        
        Returns:
            Path to generated audio file
        """
        cleaned_text = self.clean_text_for_tts(text)
        
        unique_id = str(uuid.uuid4())[:8]
        filename = f"audio_{chunk_index}_{unique_id}.mp3"
        output_path = self.output_dir / filename
        
        print(f"\nGenerating audio {chunk_index}...")
        print(f"   Section: {section}")
        print(f"   Title: {title[:60]}..." if len(title) > 60 else f"   Title: {title}")
        
        try:
            communicate = edge_tts.Communicate(
                text=cleaned_text, voice=self.voice, rate='+0%', pitch='+0Hz'
            )
            await communicate.save(str(output_path))
            
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"   Saved: {output_path.name} ({output_path.stat().st_size / 1024:.1f} KB)")
                return str(output_path)
            else:
                raise Exception("Generated file is empty or missing")
                
        except Exception as e:
            print(f"   Error generating chunk {chunk_index}: {e}")
            raise
    
    async def process_narration_file_async(self, json_path: str) -> List[str]:
        """
        Process entire narration JSON file asynchronously and in parallel.
        
        Returns:
            List of paths to successfully generated audio files
        """
        print("="*70)
        print("CRYSTAL-CLEAR NARRATION AUDIO GENERATOR (Edge TTS)")
        print("="*70)
        
        narrations = self.load_narration_json(json_path)
        if not narrations:
            print("No narration data found. Exiting.")
            return []
            
        print(f"\nLoaded {len(narrations)} narration chunks from {json_path}")
        print(f"Output directory: {self.output_dir}")
        
        # Create a list of tasks to run concurrently
        print(f"\nCreating {len(narrations)} audio generation tasks...")
        tasks = []
        for idx, chunk in enumerate(narrations):
            narration_script = chunk.get('narration_script', '')
            if not narration_script:
                print(f"\nWarning: Empty narration script for chunk {idx}. Skipping.")
                continue
            
            tasks.append(
                self.generate_audio_async(
                    text=narration_script,
                    chunk_index=idx,
                    section=chunk.get('section', 'Unknown'),
                    title=chunk.get('title', 'Untitled')
                )
            )

        print(f"Running {len(tasks)} tasks in parallel...")
        # Run tasks concurrently, collecting all results (even exceptions)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        audio_files = []
        failed_chunks = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   Task for chunk {idx} failed: {result}")
                failed_chunks.append(idx)
            else:
                audio_files.append(result)
        
        print("\n" + "="*70)
        print(f"COMPLETE: Generated {len(audio_files)}/{len(tasks)} audio files")
        
        if failed_chunks:
            print(f"Failed chunks: {failed_chunks}")
        
        print(f"All files saved to: {self.output_dir.absolute()}")
        print("="*70)
        
        return audio_files

    def merge_audio_files(self, audio_files: List[str]) -> str:
        """
        Merges a list of audio files into a single MP3 using FFmpeg.
        
        Args:
            audio_files: A list of string paths to the audio files to merge.
                         
        Returns:
            The path to the final merged audio file, or None if merging failed.
        """
        if not audio_files:
            print("Audio merge skipped: No files to merge.")
            return None
            
        print("\n" + "="*70)
        print(f"Merging {len(audio_files)} audio files using FFmpeg...")

        # Create a temporary file list for FFmpeg
        
        # Sort files by chunk index ("audio_<index>_...") to ensure correct order.
        try:
            sorted_files = sorted(audio_files, key=lambda p: int(Path(p).name.split('_')[1]))
            print("   Files sorted by chunk index.")
        except Exception as e:
            print(f"   Warning: Could not sort files by chunk index ({e}). Merging in original order.")
            sorted_files = audio_files
        
        # Create a temporary file list in the output directory
        list_filename = self.output_dir / "mergelist.txt"
        
        try:
            with open(list_filename, 'w', encoding='utf-8') as f:
                for file_path in sorted_files:
                    # Use absolute paths and 'file' keyword for ffmpeg
                    f.write(f"file '{Path(file_path).resolve()}'\n")
            
            # Prepare the FFmpeg command
            merge_uuid = str(uuid.uuid4())[:8]
            merged_filename = f"audio_merge_{merge_uuid}.mp3"
            merged_output_path = self.output_dir / merged_filename
            
            ffmpeg_command = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_filename.resolve()),
                "-c", "copy",
                str(merged_output_path.resolve())
            ]
            
            print(f"   Exporting merged file: {merged_filename}...")
            
            # Run the FFmpeg command
            result = subprocess.run(ffmpeg_command, 
                                    capture_output=True, 
                                    text=True, 
                                    check=True)

            print(f"   Merge complete. File saved as:")
            print(f"   {merged_output_path.absolute()}")
            print("="*70)
            
            return str(merged_output_path)

        except FileNotFoundError:
            print("   FATAL ERROR: 'ffmpeg' command not found.")
            print("   Please install FFmpeg: 'brew install ffmpeg'")
            return None
        except subprocess.CalledProcessError as e:
            print(f"   Error during FFmpeg merge process:")
            print(e.stderr) # Print the error from ffmpeg
            return None
        except Exception as e:
            print(f"   An unexpected error occurred during merge: {e}")
            return None
        finally:
            # Clean up the temporary list file
            if os.path.exists(list_filename):
                os.remove(list_filename)

    def process_narration_file(self, json_path: str) -> (List[str], str):
        """
        Synchronous wrapper for async processing and merging.
        
        Returns:
            Tuple of: (List of individual file paths, Path to merged file)
        """
        individual_files = asyncio.run(self.process_narration_file_async(json_path))
        
        if not individual_files:
            print("No individual files were generated. Skipping merge.")
            return individual_files, None
            
        merged_file_path = self.merge_audio_files(individual_files)
        return individual_files, merged_file_path


def main():
    """Main execution function"""
    
    # --- Path Configuration ---
    # Get the directory where this script is located
    SCRIPT_DIR = Path(__file__).parent.resolve()
    # Go up to the project root (assuming script is in 'src/utils' or similar)
    PROJECT_ROOT = SCRIPT_DIR.parent.parent
    
    # Use PROJECT_ROOT to build absolute paths
    JSON_INPUT_PATH = PROJECT_ROOT / "src/utils/narrationOutput.json"
    OUTPUT_DIR = PROJECT_ROOT / "src/static/outputs/audio"
    
    # Voice options: 'male_professional', 'female_professional', 
    #                'male_narrator', 'female_narrator'
    VOICE_TYPE = 'male_narrator'
    
    print("\nStarting Narration Audio Generation...")
    print(f"Input: {JSON_INPUT_PATH}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Voice: {VOICE_TYPE}\n")
    
    # Initialize generator
    generator = EdgeTTSNarrationGenerator(
        output_base_dir=str(OUTPUT_DIR),
        voice=VOICE_TYPE
    )
    
    # Process and print results
    try:
        audio_files, merged_file = generator.process_narration_file(str(JSON_INPUT_PATH))
        
        if audio_files:
            print("\nGenerated Individual Audio Files:")
            print("-" * 70)
            for i, audio_file in enumerate(audio_files, 1):
                file_path = Path(audio_file)
                size_kb = file_path.stat().st_size / 1024
                print(f"{i:2d}. {file_path.name:40s} ({size_kb:6.1f} KB)")
            print("-" * 70)
        
        if merged_file:
            print("\nFinal Merged File:")
            print("-" * 70)
            file_path = Path(merged_file)
            size_kb = file_path.stat().st_size / 1024
            print(f"   {file_path.name:40s} ({size_kb:6.1f} KB)")
            print("-" * 70)
            print(f"Success! All files ready for use.\n")
        else:
            print("Process finished, but no merged file was created.")
            
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}\n")
        raise


if __name__ == "__main__":
    main()
