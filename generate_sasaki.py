"""佐々木さん（31歳・現場監督・入社4年目）のポートレート画像を gpt-image-2 で生成するスクリプト"""
import base64
import os
from pathlib import Path

from openai import OpenAI

ENV_PATH = Path.home() / ".claude" / "credentials" / ".env"
for line in ENV_PATH.read_text().splitlines():
    if line.startswith("openai_apikey="):
        os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1].strip()
        break

client = OpenAI()

PROMPT = """A cinematic, high-contrast documentary-style portrait of a 31-year-old Japanese male demolition site supervisor in Japan.

Subject:
- Japanese man, 31 years old, lean, sun-tanned skin, short black hair slightly messy from a hard hat, masculine and confident face with a slight calm smile
- Wearing a navy or charcoal Japanese workwear jacket (作業着 / 'tobi'-style) with subtle dust on the shoulders
- A white safety helmet either held casually under his right arm or set down beside him, with a small sticker
- Heavy-duty work gloves visible, slightly worn

Setting:
- Standing on a Japanese demolition site at golden-hour late afternoon
- Background: partially demolished concrete wall, exposed rebar, scattered concrete debris and a distant excavator silhouette, slightly out of focus
- Soft warm sunlight from the side, dust particles floating in the light beam
- Japanese urban/suburban scenery feel (Aichi region, regional Japanese building style)

Mood / Style:
- Quiet pride, dignity, working-class hero vibe — matches the headline 'I can feed myself with these two arms. That's pride.'
- Cinematic color grading: warm highlights, deep cool shadows, slight teal-orange split tone, natural skin tones
- Shallow depth of field, 50mm lens look, slight film grain
- Photorealistic, magazine editorial quality, NOT illustration, NOT anime
- 9:16 vertical portrait orientation suitable for a recruitment landing page

No text, no logos, no watermark, no captions in the image."""

print("[1/2] gpt-image-2 で画像を生成中... (約30〜60秒)")
result = client.images.generate(
    model="gpt-image-2",
    prompt=PROMPT,
    size="1024x1536",
    quality="high",
    n=1,
)

image_b64 = result.data[0].b64_json
output_path = Path(__file__).parent / "assets" / "sasaki-portrait.jpg"
output_path.write_bytes(base64.b64decode(image_b64))

print(f"[2/2] 保存完了: {output_path}")
print(f"ファイルサイズ: {output_path.stat().st_size / 1024:.1f} KB")
