'''OpenAI gpt-4-vision example script from image file
uses pillow to resize and make png: pip install pillow'''

import base64
from io import BytesIO
from PIL import Image
import os
from openai import AzureOpenAI
from dotenv import load_dotenv  

load_dotenv(override=True)

def encode_image(image_path, max_image=512):
    with Image.open(image_path) as img:
        width, height = img.size
        max_dim = max(width, height)
        if max_dim > max_image:
            scale_factor = max_image / max_dim
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = img.resize((new_width, new_height))

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str



client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2023-12-01-preview"
)

image_file = "./images/car.png"
max_size = 512  # set to maximum dimension to allow (512=1 tile, 2048=max)
encoded_string = encode_image(image_file, max_size)

system_prompt = ("You are an expert at analyzing images with computer vision. In case of error, "
 "make a full report of the cause of: any issues in receiving, understanding, or describing images")
user = ("Describe the contents and layout of my image.")

apiresponse = client.chat.completions.with_raw_response.create(
    model="gpt-4v",
    messages=[
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user},
                {
                    "type": "image_url",
                    "image_url": {"url":
                        f"data:image/jpeg;base64,{encoded_string}"},
                },
            ],
        },
    ],
    max_tokens=500,
)
debug_sent = apiresponse.http_request.content
chat_completion = apiresponse.parse()
print(chat_completion.choices[0].message.content)
print(chat_completion.usage.model_dump())
print(
    "remaining-requests: "
    f"{apiresponse.headers.get('x-ratelimit-remaining-requests')}"
)
