run:
	python3 main.py
.PHONY: run

loader:
	python3 ./quant/loaders/base_loader.py
.PHONY: load

gpt4all:
	python3 ./quant/engines/gpt4all.py
.PHONY: gpt4all
