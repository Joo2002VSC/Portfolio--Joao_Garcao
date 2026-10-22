tudo: CorpoEntrevistaJoao.conll CorpoEntrevistaJoao-ent.txt CorpoEntrevistaJoao-keywords.txt CorpoEntrevistaJoao-nchunks.txt CorpoEntrevistaJoao-sentimento.txt


#anotar texto
CorpoEntrevistaJoao.conll : CorpoEntrevistaJoao.txt
	advconll CorpoEntrevistaJoao.txt > CorpoEntrevistaJoao.conll 

#calcular entidades
CorpoEntrevistaJoao-ent.txt  : CorpoEntrevistaJoao.conll 
	rg PROPN CorpoEntrevistaJoao.conll | sort | uniq -c | sort -n > CorpoEntrevistaJoao.txt 
    #Esta lista com noun é para os nomes normais

# Regra para gerar CorpoEntrevistaJoao-ent.txt a partir de CorpoEntrevistaJoao.conll
CorpoEntrevistaJoao-keywords.txt: CorpoEntrevistaJoao.conll
	keyterms CorpoEntrevistaJoao.txt | sort | uniq -c | sort -n > CorpoEntrevistaJoao-keywords.txt

CorpoEntrevistaJoao-nchunks.txt: CorpoEntrevistaJoao.conll
	grep -E '\b(NOUN|PROPN)\b' CorpoEntrevistaJoao.conll | cut -f1 | sort | uniq -c | sort -nr > CorpoEntrevistaJoao-nchunks.txt

CorpoEntrevistaJoao-sentimento.txt: CorpoEntrevistaJoao.txt
	python3 sentimento.py CorpoEntrevistaJoao.txt > CorpoEntrevistaJoao-sentimento.txt


