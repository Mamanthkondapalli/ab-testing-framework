.PHONY: setup examples clean

setup:
	pip install -r requirements.txt

examples:
	python examples/conversion_rate_test.py
	python examples/revenue_test.py
	python examples/engagement_test.py

clean:
	rm -rf outputs/
