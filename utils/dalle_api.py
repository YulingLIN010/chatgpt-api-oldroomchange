import openai
import os

# 請確保你在 Render 或本地有設 OPENAI_API_KEY 環境變數
openai.api_key = os.getenv("OPENAI_API_KEY")

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
