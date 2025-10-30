.PHONY: help build up down logs clean restart build-run test lint

# Default target
.DEFAULT_GOAL := help

# Color output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

# Docker configuration
DOCKER_IMAGE_NAME := ss_to_tg_video
DOCKER_CONTAINER_NAME := VideoSsToTg
DOCKER_COMPOSE_FILE := docker-compose.yaml

help: ## Show this help message
	@echo "$(GREEN)Synology Surveillance Station Video to Telegram$(NC)"
	@echo "$(YELLOW)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

check-env: ## Check if .env file exists
	@if [ ! -f .env ]; then \
		echo "$(RED)Error: .env file not found!$(NC)"; \
		echo "$(YELLOW)Run: cp .env.example .env$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN).env file found!$(NC)"

build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(NC)"
	docker build -t $(DOCKER_IMAGE_NAME):latest .
	@echo "$(GREEN)Build completed!$(NC)"

build-run: build up ## Build and start containers

up: check-env ## Start containers with docker-compose
	@echo "$(YELLOW)Starting containers...$(NC)"
	docker-compose -f $(DOCKER_COMPOSE_FILE) up -d
	@echo "$(GREEN)Containers started!$(NC)"
	@echo "$(YELLOW)Container logs:$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) logs --tail=20

down: ## Stop and remove containers
	@echo "$(YELLOW)Stopping containers...$(NC)"
	docker-compose -f $(DOCKER_COMPOSE_FILE) down
	@echo "$(GREEN)Containers stopped!$(NC)"

restart: ## Restart containers
	@echo "$(YELLOW)Restarting containers...$(NC)"
	docker-compose -f $(DOCKER_COMPOSE_FILE) restart
	@echo "$(GREEN)Containers restarted!$(NC)"

logs: ## View container logs
	@docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f

logs-tail: ## View last 50 lines of logs
	@docker-compose -f $(DOCKER_COMPOSE_FILE) logs --tail=50

status: ## Show container status
	@echo "$(YELLOW)Container Status:$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) ps

shell: ## Open shell in running container
	@docker-compose -f $(DOCKER_COMPOSE_FILE) exec $(DOCKER_CONTAINER_NAME) /bin/sh

clean: ## Remove containers, images and volumes
	@echo "$(RED)Removing containers, images and volumes...$(NC)"
	docker-compose -f $(DOCKER_COMPOSE_FILE) down -v
	docker rmi $(DOCKER_IMAGE_NAME):latest 2>/dev/null || true
	@echo "$(GREEN)Cleanup completed!$(NC)"

clean-logs: ## Clean container logs
	@echo "$(YELLOW)Cleaning logs...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) logs --tail=0 2>/dev/null || true
	@echo "$(GREEN)Logs cleaned!$(NC)"

rebuild: clean build up ## Clean, rebuild, and start containers

test: ## Run tests (if available)
	@echo "$(YELLOW)Running tests...$(NC)"
	python -m pytest tests/ || echo "$(YELLOW)No tests found$(NC)"

lint: ## Run Python linter
	@echo "$(YELLOW)Running Python linter...$(NC)"
	pylint src/main.py 2>/dev/null || echo "$(YELLOW)Pylint not installed. Install with: pip install pylint$(NC)"

format: ## Format Python code
	@echo "$(YELLOW)Formatting Python code...$(NC)"
	black src/ 2>/dev/null || echo "$(YELLOW)Black not installed. Install with: pip install black$(NC)"

setup-env: ## Create .env file from template
	@if [ -f .env ]; then \
		echo "$(YELLOW).env file already exists. Skipping...$(NC)"; \
	else \
		cp .env.example .env; \
		echo "$(GREEN).env file created from .env.example$(NC)"; \
		echo "$(YELLOW)Please edit .env with your configuration$(NC)"; \
	fi

validate: ## Validate docker-compose.yaml
	@echo "$(YELLOW)Validating docker-compose.yaml...$(NC)"
	docker-compose -f $(DOCKER_COMPOSE_FILE) config > /dev/null
	@echo "$(GREEN)docker-compose.yaml is valid!$(NC)"

ps: ## Alias for status
	@make status

version: ## Show version information
	@echo "$(GREEN)Synology Surveillance Station Video to Telegram$(NC)"
	@echo "$(YELLOW)Docker version:$(NC)"
	@docker --version
	@echo "$(YELLOW)Docker Compose version:$(NC)"
	@docker-compose --version

init: setup-env validate build ## Initialize project (create .env, validate config, build image)

docs: ## Open documentation
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  - English: open README.en.md"
	@echo "  - Russian: open README.md"

push-image: ## Push Docker image to registry (requires configuration)
	@echo "$(YELLOW)Pushing Docker image...$(NC)"
	docker tag $(DOCKER_IMAGE_NAME):latest yourregistry/$(DOCKER_IMAGE_NAME):latest
	docker push yourregistry/$(DOCKER_IMAGE_NAME):latest
	@echo "$(GREEN)Image pushed!$(NC)"

save-image: ## Save Docker image to tar file
	@echo "$(YELLOW)Saving Docker image...$(NC)"
	docker save $(DOCKER_IMAGE_NAME):latest > $(DOCKER_IMAGE_NAME).tar
	@echo "$(GREEN)Image saved to $(DOCKER_IMAGE_NAME).tar$(NC)"

load-image: ## Load Docker image from tar file
	@echo "$(YELLOW)Loading Docker image...$(NC)"
	docker load < $(DOCKER_IMAGE_NAME).tar
	@echo "$(GREEN)Image loaded!$(NC)"

info: ## Show project information
	@echo "$(GREEN)Project Information:$(NC)"
	@echo "  Name: Synology Surveillance Station Video to Telegram"
	@echo "  Docker Image: $(DOCKER_IMAGE_NAME)"
	@echo "  Container Name: $(DOCKER_CONTAINER_NAME)"
	@echo "  Port: 7878"
	@echo "  Compose File: $(DOCKER_COMPOSE_FILE)"

.SILENT: help
