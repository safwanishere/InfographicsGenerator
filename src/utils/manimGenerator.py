import json, os
from openai import OpenAI
from dotenv import load_dotenv
import subprocess
from pathlib import Path

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MANIM_SYSTEM_PROMPT = """
You are an expert Manim scene generator for educational explainer videos.

## Task
You will receive a JSON object in this format:
{
  "results": [
    {
      "section": "Section 683",
      "title": "Section 683 — High Level Lighting Systems",
      "narration_script": "In this section, we’ll explore how high-level lighting systems are fabricated...",
      "source": "2021StandardSpecifications.pdf",
      "page_number": 1311
    },
    ...
  ]
}

Your task is to generate a **single Python script** compatible with **Manim Community Edition** (v0.18+)
that visually represents the content of the narration scripts as an explainer video.

### Guidelines
- Use `from manim import *`.
- Define a single Scene subclass called `Explainer(Scene)`.
- Create sequential scenes that correspond to each narration chunk.
- Display section titles, subtitles, and short bullet-point text from the narration.
- Use smooth transitions (FadeIn, Write, Transform, etc.).
- Use simple visual cues like circles, arrows, or highlights for key phrases.
- Add comments in the code indicating which narration each part corresponds to.
- Do **not** include audio or external assets.
- End with a closing fade out or title card.
- Keep visuals minimal and legible (no heavy math animation).

### Output
Return ONLY a complete valid Python script (no extra markdown, commentary, or JSON wrapper).
"""


def generate_manim_script(narration_json_path, output_dir: str = "src/static/outputs/temp"):
    with open(narration_json_path, "r") as f:
        narration_data = json.load(f)

    input_json = json.dumps(narration_data, indent=2)
    script_path = os.path.join(output_dir, f"manimScript.py")

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": MANIM_SYSTEM_PROMPT},
            {"role": "user", "content": input_json}
        ],
    )

    script_code = response.choices[0].message.content.strip()

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_code)

    return script_path



def render_manim_video(script_path: str, output_dir: str = "src/static/outputs/video"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir)

    command = [
        "manim",
        script_path,
        "Explainer",
        "-pqh",  # play, high quality
        "--media_dir", str(output_path)
    ]

    subprocess.run(command, check=True)
    # Manim will place the video under {output_dir}/videos/Explainer/1080p60/Explainer.mp4
    return list(output_path.rglob("Explainer.mp4"))[0]

