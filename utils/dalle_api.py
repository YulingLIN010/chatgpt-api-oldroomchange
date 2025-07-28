import openai
import os

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise Exception("OpenAI API key not set. 請在環境變數設 OPENAI_API_KEY")
openai.api_key = api_key

def generate_image(prompt):
    """
    使用 DALL·E 3 產生圖片。只需傳入條列英文 prompt。
    回傳圖片網址（需再下載到本地再後處理加LOGO）。
    """
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    img_url = response.data[0].url
    return img_url

