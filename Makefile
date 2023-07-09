run:
	python3 main.py
.PHONY: run

## Test porting of privateGPT
test-gpt-load:
	python3 ./loaders/loader.py
.PHONY: test-gpt-load

test-gpt-run:
	python3 ./engine/gpt4all.py
.PHONY: test-gpt-run
##############################
