format:
	poetry run python -m monoformat .

build_test_base:
	rm -fr dist repo
	poetry build
	mkdir -p repo/modelw-docker
	cp dist/* repo/modelw-docker
	./docker_dev_build.py

build_test_api: build_test_base
	cd demo/api && docker build -t modelw-base-test-api .

build_test_front: build_test_base
	cd demo/front && docker build -t modelw-base-test-front .
