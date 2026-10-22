from textblob import TextBlob
import sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    texto = f.read()

blob = TextBlob(texto)
print(blob.sentiment)
