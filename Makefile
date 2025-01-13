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

demo_run: build_test_base
	docker compose -p modelw_demo_project -f docker-compose.yaml up --build --force-recreate --abort-on-container-exit --remove-orphans | tee demo.log

demo_stop:
	docker compose -p modelw_demo_project -f docker-compose.yaml down --remove-orphans

check_release:
ifndef VERSION
	$(error VERSION is undefined)
endif

release: check_release
	git flow release start $(VERSION)
	sed -i 's/^version =.*/version = "$(VERSION)"/' pyproject.toml
	sed -i -E 's/modelw-docker==[^'"'"']+/modelw-docker==$(VERSION)/' image/Dockerfile
	git add pyproject.toml image/Dockerfile
	git commit -m "Bump version to $(VERSION)"
	git flow release finish -m "Release $(VERSION)" $(VERSION) > /dev/null
