import json
from PyPDF2 import PdfReader

def parse_json(file):
    with open(file, 'r') as f:
        content = f.read()
    return json.loads(content)

def extract(path):
    full_text = ''
    with open(path, 'rb') as f:
        pdf = PdfReader(f)
        for page in pdf.pages:
            text = page.extract_text().split('\n')
            text = ' '.join(text)
            text = text.replace(' - ', '')
            full_text += ' ' + text
    return full_text


if __name__ == '__main__':
    urls = parse_json('urls_scrapped.json')

    for vol in urls:
        for iss in vol:
            path = '\\archive\\vol_'+vol+'issue_'+iss
            full_text = extract(path)
            if any(relavent_words in full_text):
