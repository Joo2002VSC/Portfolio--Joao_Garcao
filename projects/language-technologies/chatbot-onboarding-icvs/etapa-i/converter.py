import docx

# Caminhos
input_path = r"C:\Users\gonsa\OneDrive\Desktop\chatbot\ICVS Onboarding Manual_nov25_RM_update_clean_not final.docx"
output_path = r"C:\Users\gonsa\OneDrive\Desktop\chatbot\icvs_manual.txt"

# Ler documento
doc = docx.Document(input_path)

# Extrair texto
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

# Juntar tudo num único texto
full_text = "\n\n".join(paragraphs)

# Guardar como .txt
with open(output_path, "w", encoding="utf-8") as f:
    f.write(full_text)

print("✔️ Conversão concluída!")
print("TXT criado em:", output_path)
