import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


def input_to_narration(file_path):
    
    # opening the input file
    try:
        with open(file_path, 'r') as file:
            input_data = json.load(file)
    except FileNotFoundError:
        print("input.json not found")

    input = json.dumps(input_data, indent=4)


    # Calling the OpenAI API
    client = OpenAI(api_key=api_key)

    SYSTEM_PROMPT = """
    You are a helpful assistant that converts technical specification documents into human-friendly narration scripts for explainer videos.

    ## Task
    You will receive a JSON array where each element (chunk) contains:
    {
        "section": string,
        "title": string,
        "content": string,
        "source": string,
        "page_number": integer
    }

    Your job is to generate a new JSON array with the *same number of elements*.  
    For each input chunk, create a corresponding output object that includes:
    {
        "section": <same as input>,
        "title": <same as input>,
        "narration_script": <string narration script based on the content>
    }

    ## Guidelines for Narration Script
    - Rewrite the "content" in a way that sounds **clear, natural, and conversational**, as if narrated in a professional explainer video.
    - Avoid technical jargon unless essential. Simplify and clarify the meaning while maintaining accuracy.
    - Use smooth transitions and natural pacing cues like "Let’s take a look at...", "In this section...", or "Essentially, this means that...".
    - Do **not** just rephrase sentences — interpret the content and present it in a way that explains the key ideas logically.
    - Do not include bullet points or formatting, just plain narration text.
    - Each narration should be **1–3 short paragraphs** long depending on the content length.
    - Never invent details or add information not present in the input.

    ## Output Format
    Return a valid JSON object with the following structure:
    [
        {
        "section": "...",
        "title": "...",
        "narration_script": "...",
        },
        ...
    ]

    Ensure the response is a **single valid JSON object** with no extra commentary or text outside the JSON.
    """


    response = client.chat.completions.create(
        model="gpt-5",
                
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": input}
        ],
    )

    response = response.choices[0].message.content


    # Parse the JSON and save to file
    try:
        narration_output = json.loads(response)
    except json.JSONDecodeError:
        print("Error: Model output was not valid JSON.")
        narration_output = {"results": []}

    output_file = "src/utils/narrationOutput.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(narration_output, f, indent=4, ensure_ascii=False)

    print(f"Narration JSON saved to {output_file}")