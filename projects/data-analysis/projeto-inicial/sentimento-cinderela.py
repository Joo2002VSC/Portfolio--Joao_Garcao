import os
from textblob import TextBlob
import matplotlib.pyplot as plt

# Caminho para o arquivo
file_path = '/Users/joaogarcao/Desktop/MHD/II Semestre/AVD/Projeto/Cinderela.txt'

def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

# Divide o texto por parágrafos (separados por linha vazia)
def split_text_into_paragraphs(text):
    # Divide em parágrafos, remove espaços extras e ignora vazios
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs

def analyze_file_sentiment_by_paragraph(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    paragraphs = split_text_into_paragraphs(text)
    print(f"Total de parágrafos: {len(paragraphs)}")

    sentiments = []
    for i, paragraph in enumerate(paragraphs):
        sentiment = analyze_sentiment(paragraph)
        sentiments.append((i + 1, sentiment))

    return sentiments

def generate_sentiment_graph(sentiments, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    paragraph_labels = [str(item[0]) for item in sentiments]
    sentiment_values = [item[1] for item in sentiments]

    plt.figure(figsize=(12, 6))
    plt.bar(paragraph_labels, sentiment_values, color=['skyblue' if x >= 0 else 'salmon' for x in sentiment_values])
    plt.xlabel('Parágrafo')
    plt.ylabel('Polaridade do Sentimento')
    plt.title('Análise de Sentimentos por Parágrafo')
    plt.xticks(rotation=90)
    plt.ylim(-1, 1)
    plt.tight_layout()

    output_file = os.path.join(output_path, 'sentiment_analysis_paragraphs.png')
    plt.savefig(output_file)
    plt.close()
    print(f"Gráfico salvo em: {output_file}")

# Caminho de saída
output_path = '/Users/joaogarcao/Desktop/MHD/II Semestre/AVD/Projeto'

# Executa a análise
sentiments = analyze_file_sentiment_by_paragraph(file_path)
generate_sentiment_graph(sentiments, output_path)
