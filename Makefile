clean:
	find -name "*.pyc" -delete

test:
	nosetests -s
