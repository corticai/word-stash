
DOCKER_NETWORK=cicd
ENVIRONMENT_NAME?=dev
AWS_PROFILE?=default
LAMBDA_PACKAGES_S3_BUCKET?=word-stash-lambda-packages-bucket
IMPLETER_CONVERTERS_LAMBDA_LAYER_ZIP_S3_KEY?=impleter_converters_lambda_layer.zip
IMPLETER_CONVERTERS_SOURCE_ZIP_S3_KEY?=impleter_converters_lambda.zip
IMPLETER_PARSERS_LAMBDA_LAYER_ZIP_S3_KEY?=impleter_parsers_lambda_layer.zip
IMPLETER_PARSERS_SOURCE_ZIP_S3_KEY?=impleter_parsers_lambda.zip
IMPLETER_PUBLISHERS_LAMBDA_LAYER_ZIP_S3_KEY?=impleter_publishers_lambda_layer.zip
IMPLETER_PUBLISHERS_SOURCE_ZIP_S3_KEY?=impleter_publishers_lambda.zip
$(eval BASE_NAME=$(shell basename `pwd`))

test:
	(cd impleter/converters; make BASE_NAME=$(BASE_NAME) ENVIRONMENT_NAME=$(ENVIRONMENT_NAME) test)
	(cd impleter/parsers; make BASE_NAME=$(BASE_NAME) ENVIRONMENT_NAME=$(ENVIRONMENT_NAME) test)

start-local-word-stash:
	docker-compose -f ./local-dependencies/opensearch/docker-compose.yaml up -d
	until $$(curl -XGET https://localhost:9200 -u admin:admin --insecure) ; do \
		printf '.' ; \
		sleep 5 ; \
	done

start-local: start-local-word-stash

stop-local-word-stash:
	docker-compose -f ./local-dependencies/opensearch/docker-compose.yaml down

stop-local: stop-local-word-stash

validate-lambda-packages-cf:
	aws cloudformation validate-template \
		--template-body file://./cloudformation/$(BASE_NAME)-lambda-packages-$(ENVIRONMENT_NAME).cf.yaml

deploy-lambda-packages-cf:
	aws cloudformation deploy \
		--template-file ./cloudformation/$(BASE_NAME)-lambda-packages-$(ENVIRONMENT_NAME).cf.yaml \
		--stack-name $(BASE_NAME)-lambda-packages-$(ENVIRONMENT_NAME) \
		--parameter-overrides BaseName=$(BASE_NAME) \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset

build-impleter-converters-lambda-packages:
	docker build -t impleter-converters-package-artifacts -f local-dependencies/lambda-packager/impleter/converters/Dockerfile .

build-impleter-parsers-lambda-packages:
	docker build -t impleter-parsers-package-artifacts -f local-dependencies/lambda-packager/impleter/parsers/Dockerfile .

build-impleter-publishers-lambda-packages:
	docker build -t impleter-parsers-package-artifacts -f local-dependencies/lambda-packager/impleter/publishers/Dockerfile .

build-impleter-lambda-packages: build-impleter-converters-lambda-packages build-impleter-parsers-lambda-packages build-impleter-publishers-lambda-packages

create-and-upload-impleter-converters-lambda-packages-from-local: build-impleter-converters-lambda-packages
	docker run --rm -v ~/.aws:/root/.aws:ro -it \
			-e AWS_PROFILE=$(AWS_PROFILE) \
			-e LAMBDA_PACKAGES_S3_BUCKET=$(LAMBDA_PACKAGES_S3_BUCKET) \
			-e IMPLETER_CONVERTERS_LAMBDA_LAYER_ZIP_S3_KEY=$(IMPLETER_CONVERTERS_LAMBDA_LAYER_ZIP_S3_KEY) \
			-e IMPLETER_CONVERTERS_SOURCE_ZIP_S3_KEY=$(IMPLETER_CONVERTERS_SOURCE_ZIP_S3_KEY) \
		impleter-converters-package-artifacts

create-and-upload-impleter-parsers-lambda-packages-from-local: build-impleter-parsers-lambda-packages
	docker run --rm -v ~/.aws:/root/.aws:ro -it \
			-e AWS_PROFILE=$(AWS_PROFILE) \
			-e LAMBDA_PACKAGES_S3_BUCKET=$(LAMBDA_PACKAGES_S3_BUCKET) \
			-e IMPLETER_PARSERS_LAMBDA_LAYER_ZIP_S3_KEY=$(IMPLETER_PARSERS_LAMBDA_LAYER_ZIP_S3_KEY) \
			-e IMPLETER_PARSERS_SOURCE_ZIP_S3_KEY=$(IMPLETER_PARSERS_SOURCE_ZIP_S3_KEY) \
		impleter-parsers-package-artifacts

create-and-upload-impleter-publishers-lambda-packages-from-local: build-impleter-publishers-lambda-packages
	docker run --rm -v ~/.aws:/root/.aws:ro -it \
			-e AWS_PROFILE=$(AWS_PROFILE) \
			-e LAMBDA_PACKAGES_S3_BUCKET=$(LAMBDA_PACKAGES_S3_BUCKET) \
			-e IMPLETER_PUBLISHERS_LAMBDA_LAYER_ZIP_S3_KEY=$(IMPLETER_PUBLISHERS_LAMBDA_LAYER_ZIP_S3_KEY) \
			-e IMPLETER_PUBLISHERS_SOURCE_ZIP_S3_KEY=$(IMPLETER_PUBLISHERS_SOURCE_ZIP_S3_KEY) \
		impleter-parsers-package-artifacts

create-and-upload-impleter-lambda-packages-from-local: create-and-upload-impleter-converters-lambda-packages-from-local create-and-upload-impleter-parsers-lambda-packages-from-local create-and-upload-impleter-publishers-lambda-packages-from-local

create-and-upload-impleter-converters-lambda-packages: build-impleter-converters-lambda-packages
	docker run --rm \
			-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
			-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
			-e AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) \
			-e AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
			-e LAMBDA_PACKAGES_S3_BUCKET=$(LAMBDA_PACKAGES_S3_BUCKET) \
			-e IMPLETER_CONVERTERS_LAMBDA_LAYER_ZIP_S3_KEY=$(IMPLETER_CONVERTERS_LAMBDA_LAYER_ZIP_S3_KEY) \
			-e IMPLETER_CONVERTERS_SOURCE_ZIP_S3_KEY=$(IMPLETER_CONVERTERS_SOURCE_ZIP_S3_KEY) \
		impleter-converters-package-artifacts

create-and-upload-impleter-parsers-lambda-packages: build-impleter-parsers-lambda-packages
	docker run --rm \
			-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
			-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
			-e AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) \
			-e AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
			-e LAMBDA_PACKAGES_S3_BUCKET=$(LAMBDA_PACKAGES_S3_BUCKET) \
			-e IMPLETER_PARSERS_LAMBDA_LAYER_ZIP_S3_KEY=$(IMPLETER_PARSERS_LAMBDA_LAYER_ZIP_S3_KEY) \
			-e IMPLETER_PARSERS_SOURCE_ZIP_S3_KEY=$(IMPLETER_PARSERS_SOURCE_ZIP_S3_KEY) \
		impleter-parsers-package-artifacts

create-and-upload-impleter-publishers-lambda-packages: build-impleter-publishers-lambda-packages
	docker run --rm \
			-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
			-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
			-e AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) \
			-e AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
			-e LAMBDA_PACKAGES_S3_BUCKET=$(LAMBDA_PACKAGES_S3_BUCKET) \
			-e IMPLETER_PUBLISHERS_LAMBDA_LAYER_ZIP_S3_KEY=$(IMPLETER_PUBLISHERS_LAMBDA_LAYER_ZIP_S3_KEY) \
			-e IMPLETER_PUBLISHERS_SOURCE_ZIP_S3_KEY=$(IMPLETER_PUBLISHERS_SOURCE_ZIP_S3_KEY) \
		impleter-parsers-package-artifacts

create-and-upload-impleter-lambda-packages: create-and-upload-impleter-converters-lambda-packages create-and-upload-impleter-parsers-lambda-packages create-and-upload-impleter-publishers-lambda-packages

validate-word-stash-db-cf:
	aws cloudformation validate-template \
		--template-body file://./cloudformation/$(BASE_NAME)-db-${ENVIRONMENT_NAME}.cf.yaml

validate-word-stash-parsers-cf:
	aws cloudformation validate-template \
		--template-body file://./cloudformation/$(BASE_NAME)-parsers-${ENVIRONMENT_NAME}.cf.yaml

validate-word-stash-converters-cf:
	aws cloudformation validate-template \
		--template-body file://./cloudformation/$(BASE_NAME)-converters-${ENVIRONMENT_NAME}.cf.yaml

validate-word-stash-publishers-cf:
	aws cloudformation validate-template \
		--template-body file://./cloudformation/$(BASE_NAME)-publishers-${ENVIRONMENT_NAME}.cf.yaml

deploy-word-stash-db-cf:
	aws cloudformation deploy \
		--template-file ./cloudformation/$(BASE_NAME)-db-${ENVIRONMENT_NAME}.cf.yaml \
		--stack-name $(BASE_NAME)-db-$(ENVIRONMENT_NAME) \
		--parameter-overrides $(shell cat config/$(ENVIRONMENT_NAME)/$(BASE_NAME)-db.cf.conf) \
			BaseName=$(BASE_NAME)-db-${ENVIRONMENT_NAME} \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset

deploy-word-stash-parsers-cf:
	aws cloudformation deploy \
		--template-file ./cloudformation/$(BASE_NAME)-parsers-${ENVIRONMENT_NAME}.cf.yaml \
		--stack-name $(BASE_NAME)-parsers-$(ENVIRONMENT_NAME) \
		--parameter-overrides $(shell cat config/$(ENVIRONMENT_NAME)/$(BASE_NAME)-parsers.cf.conf) \
			BaseName=$(BASE_NAME)-parsers-${ENVIRONMENT_NAME} \
			ImpleterParsersLambdaLayerZipS3Key=$(IMPLETER_PARSERS_LAMBDA_LAYER_ZIP_S3_KEY) \
			ImpleterParsersLambdaZipS3Key=$(IMPLETER_PARSERS_SOURCE_ZIP_S3_KEY) \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset

deploy-word-stash-converters-cf:
	aws cloudformation deploy \
		--template-file ./cloudformation/$(BASE_NAME)-converters-${ENVIRONMENT_NAME}.cf.yaml \
		--stack-name $(BASE_NAME)-converters-$(ENVIRONMENT_NAME) \
		--parameter-overrides $(shell cat config/$(ENVIRONMENT_NAME)/$(BASE_NAME)-converters.cf.conf) \
			BaseName=$(BASE_NAME)-converters-${ENVIRONMENT_NAME} \
			ImpleterConvertersLambdaLayerZipS3Key=$(IMPLETER_CONVERTERS_LAMBDA_LAYER_ZIP_S3_KEY) \
			ImpleterConvertersLambdaZipS3Key=$(IMPLETER_CONVERTERS_SOURCE_ZIP_S3_KEY) \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset

deploy-word-stash-publishers-cf:
	aws cloudformation deploy \
		--template-file ./cloudformation/$(BASE_NAME)-publishers-${ENVIRONMENT_NAME}.cf.yaml \
		--stack-name $(BASE_NAME)-publishers-$(ENVIRONMENT_NAME) \
		--parameter-overrides $(shell cat config/$(ENVIRONMENT_NAME)/$(BASE_NAME)-publishers.cf.conf) \
			BaseName=$(BASE_NAME)-publishers-${ENVIRONMENT_NAME} \
			ImpleterPublishersLambdaLayerZipS3Key=$(IMPLETER_PUBLISHERS_LAMBDA_LAYER_ZIP_S3_KEY) \
			ImpleterPublishersLambdaZipS3Key=$(IMPLETER_PUBLISHERS_SOURCE_ZIP_S3_KEY) \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset

validate-word-stash-cf: validate-word-stash-db-cf validate-word-stash-parsers-cf validate-word-stash-converters-cf validate-word-stash-publishers-cf

create-and-upload-lambda-packages: create-and-upload-impleter-lambda-packages

deploy-word-stash-cf: deploy-word-stash-db-cf deploy-word-stash-parsers-cf deploy-word-stash-converters-cf deploy-word-stash-publishers-cf

deploy-local: deploy-lambda-packages-cf create-and-upload-impleter-lambda-packages-from-local deploy-word-stash-cf

deploy: deploy-lambda-packages-cf create-and-upload-impleter-lambda-packages deploy-word-stash-cf
