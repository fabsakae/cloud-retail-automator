#!/bin/bash
# Executa análise de segurança estática na infraestrutura Terraform
echo "🔍 Iniciando scan de segurança com Checkov..."
docker run --tty --volume $(pwd)/infra:/tf bridgecrew/checkov --directory /tf