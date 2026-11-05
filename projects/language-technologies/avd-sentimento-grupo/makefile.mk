all: noun_chunks collocations lemas ttr sentiment graphs

noun_chunks:
	python3 extract_noun_chunks.py

collocations:
	python3 collocations.py

lemas:
	python3 extract_lemmas.py

ttr:
	python3 analyze_ttr.py

sentiment:
	python3 sentiment_analysis.py

clean_graphs:
	rm -rf Graficos/*

graphs: clean_graphs
	python3 generate_graphs.py
