# make build   # docker build
# make run     # docker run with .env + mounted key
# make deploy  # build+deploy to Cloud Run and print the URL

SHELL := /bin/bash

# ---- Config ----
PROJECT_ID ?= parsely-studio
REGION ?= us-west1
SERVICE ?= parsely-studio
REPO ?= app
TAG ?= $(shell date +%Y%m%d-%H%M%S)
IMAGE := $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO)/$(SERVICE):$(TAG)
ENV_DOCKER ?= .env
PORT ?= 8080
LOCAL_NAME := $(SERVICE)-local

.PHONY: help build run stop logs gcp-init gcp-build gcp-deploy gcp-url deploy gcp-set gcp-logs dev

help: ## List commands
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS=":.*?## "}; {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}'

# ---- Local docker ----
build: ## Build local image
	docker build -t $(SERVICE):local .

run: ## Run locally (maps $(PORT)->8080) with .env and mounted key
	docker run --rm --name $(LOCAL_NAME) -p $(PORT):8080 --env-file $(ENV_DOCKER) \
		-v $$HOME/.secrets/vision-key.json:/secrets/vision-key.json:ro \
		$(SERVICE):local

stop: ## Stop the local container
	-@docker rm -f $(LOCAL_NAME) 2>/dev/null || true

logs: ## Tail logs from the local container
	@docker logs -f $(LOCAL_NAME)

# ---- GCP (Artifact Registry + Cloud Run) ----
gcp-set: ## Set gcloud project/region
	gcloud config set project $(PROJECT_ID)
	gcloud config set run/region $(REGION)

gcp-init: ## One-time: enable APIs & create Artifact Registry repo
	gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com vision.googleapis.com
	gcloud artifacts repositories create $(REPO) --repository-format=docker --location=$(REGION) --description="App images" || true

gcp-build: ## Build & push image via Cloud Build
	gcloud builds submit --tag $(IMAGE)

gcp-deploy: ## Deploy to Cloud Run
	gcloud run deploy $(SERVICE) --image $(IMAGE) --region $(REGION) --memory=1Gi \
		--allow-unauthenticated --port 8080 \
		--set-secrets=OPENROUTER_API_KEY=openrouter-api-key:latest

gcp-url: ## Print service URL
	@gcloud run services describe $(SERVICE) --region $(REGION) --format='value(status.url)'

gcp-logs: ## Stream Cloud Run logs
	gcloud  beta run services logs tail $(SERVICE) --region $(REGION) --verbosity=debug

deploy: gcp-build gcp-deploy gcp-url ## Build, deploy, print URL

dev:
	poetry run dev
