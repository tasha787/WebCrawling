import re
from html import unescape
import html



def clean_text(text):
    if text:
        # text = unescape(text)
        # text = re.sub(r'<.*?>', '', text)
        # text = text.strip()
        # text = re.sub(r'\s+', ' ', text)
           # Unescape HTML entities
        text = unescape(text)
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'%[0-9A-Fa-f]{2}', lambda x: chr(int(x.group(0)[1:], 16)), text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x20-\x7E]+', '', text)
        text = re.sub(r'[\"\'\(\)\[\]{}<>]', '', text)
        text = text.lower()
        text = re.sub(r'[,.!?;:]', '', text)
        text = re.sub(r'\s+[,.!?;:]\s+', ' ', text)
    return text

def barcode_type(string):
    length= len(string)
    if length == 13 or length == 8:
        return "EAN"
    elif  length == 12 or length == 11:
        return "UPC"
    elif length == 14:
        return "GTIN"

    # def clean_text(self, text):
    #     if not text:
    #         return ''
    #     text = html.unescape(text)
    #     text = text.encode().decode('unicode_escape')
    #     text = re.sub(r'\\"', '"', text)
    #     text = str(text.encode('ascii', 'ignore')).replace("\\'", "'").replace('\\"', '"').replace("\"", '"').replace("\'", "'").replace("&amp;", "&").replace("\n", "").replace("00bd", "").replace("00be", "").replace("00bc", "").replace("003C", '<').replace("003E", '>')
    #     text_characters = re.findall(r'(\\[a-z])', text)
    #     for x in text_characters:
    #         text = text.replace(x, ' ')
    #     text = re.sub(r'<style.*?</style>', ' ', text, flags=re.DOTALL)
    #     text = re.sub(r'\b(table|th|td)\b[^<]*?>', ' ', text, flags=re.IGNORECASE)
    #     CLEANR = re.compile('<.*?>')
    #     text = re.sub(CLEANR, ' ', text)
    #     html_char = re.findall(r'(&.{1,10};)', text)
    #     for x in html_char:
    #         text = text.replace(x, ' ')
    #     if text:
    #         text = text.replace("  ", " ").replace("\\", " ")
    #         text = " ".join(text.split())
    #     text = text.replace("Description", "")
    #     text = text[2:]
    #     text = text[:-1]
    #     return text.strip()
