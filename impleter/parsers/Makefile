DOCKERFILE_PATH=../../local-dependencies/tester/impleter/Dockerfile

build-test:
	docker build -t $(BASE_NAME)-$(ENVIRONMENT_NAME)-parsers-test:latest -f $(DOCKERFILE_PATH) .

test: build-test
	docker run --rm $(BASE_NAME)-$(ENVIRONMENT_NAME)-parsers-test:latest pytest
	docker image rm -f $(BASE_NAME)-$(ENVIRONMENT_NAME)-parsers-test
