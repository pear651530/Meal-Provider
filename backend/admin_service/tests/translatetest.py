import asyncio
from googletrans import Translator

async def test_translation():
    translator = Translator()

    en_text = "Fried Rice"
    zh_tw_result = await translator.translate(en_text, dest='zh-TW')
    print(f'英文 "{en_text}" 翻譯成繁體中文是: {zh_tw_result.text}')

    en_result = await translator.translate(zh_tw_result.text, dest='en')
    print(f'繁體中文 "{zh_tw_result.text}" 翻譯回英文是: {en_result.text}')

if __name__ == "__main__":
    asyncio.run(test_translation())
