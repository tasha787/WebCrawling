import re
from html import unescape



def clean_text(text):
    if text:
        text = unescape(text)
        text = re.sub(r'<.*?>', '', text)
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
    return text

def barcode_type(string):
    length= len(string)
    if length == 13 or length == 8:
        return "EAN"
    elif  length == 12 or length == 11:
        return "UPC"
    elif length == 14:
        return "GTIN"
