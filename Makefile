run:
	python3 main.py
.PHONY: run

## Test porting of privateGPT
test-loader:
	python3 ./quant/loaders/base_loader.py
.PHONY: test-gpt-load

test-run:
	python3 ./engine/gpt4all.py
.PHONY: test-gpt-run
##############################
