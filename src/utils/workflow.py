from inputToNarration import input_to_narration
from manimGenerator import generate_manim_script, render_manim_video

# testing inputToNarration.py
# input_to_narration('src/utils/standards.json')


# testing manimGenerator.py
narration_json_path = 'src/utils/narrationOutput.json'
generate_manim_script(narration_json_path)
# render_manim_video('src/static/outputs/temp/manimScript.py')