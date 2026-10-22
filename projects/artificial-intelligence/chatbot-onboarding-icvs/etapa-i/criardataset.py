import re
import pandas as pd

# Caminhos
input_path = r"C:\Users\gonsa\OneDrive\Desktop\chatbot\etapa_i\icvs_manual.txt"
output_path = r"C:\Users\gonsa\OneDrive\Desktop\chatbot\icvs_dataset.csv"

def remove_emoji(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0000200D"             # zero width joiner
        "\U00002300-\U000023FF"  # technical symbols
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

# Ler o arquivo de texto
with open(input_path, "r", encoding="utf-8") as f:
    lines = [remove_emoji(line.strip()) for line in f.readlines() if line.strip()]

# Função para identificar títulos
def is_heading(line):
    # Heading típico: curto, pode estar todo em maiúsculas, ou começa como título
    return (
        line.isupper() and len(line.split()) <= 10
    ) or re.match(r'^[A-Z][A-Za-z ]{4,}$', line)

dataset = []
current_section = "General"

for line in lines:
    if is_heading(line):
        current_section = line
    else:
        dataset.append({"section": current_section, "text": line})

df = pd.DataFrame(dataset)

# ============================
# JUNTAR PARÁGRAFOS CURTOS
# ============================
merged = []
buffer = ""
last_section = None

for idx, row in df.iterrows():
    sec = row["section"]
    txt = row["text"]

    # Mudança de secção → guardar buffer
    if sec != last_section:
        if buffer:
            merged.append({"section": last_section, "text": buffer.strip()})
            buffer = ""
        last_section = sec

    # Acumular parágrafos curtos
    if len(txt) < 80:
        buffer += " " + txt
    else:
        if buffer:
            merged.append({"section": sec, "text": buffer.strip()})
            buffer = ""
        merged.append({"section": sec, "text": txt})

# Guardar buffer final
if buffer:
    merged.append({"section": last_section, "text": buffer.strip()})

df_final = pd.DataFrame(merged)

# Exportar o dataset final
df_final.to_csv(output_path, index=False, encoding="utf-8")

print("Dataset criado com sucesso!")
print("Local:", output_path)
print("\nPrimeiras linhas:")
print(df_final.head())
print("\nNúmero total de entradas:", len(df_final))
