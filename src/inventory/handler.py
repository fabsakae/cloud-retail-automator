"""
Cloud Retail Automator — Inventory Handler
Lambda responsável por gerenciar operações de estoque no DynamoDB.
Operações suportadas: put_item, get_item, list_items, check_low_stock
"""

import json
import logging
import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

# Configuração do logger — aparece no CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cliente DynamoDB — usa variável de ambiente para o nome da tabela
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "cloud-retail-automator-inventory")
table = dynamodb.Table(TABLE_NAME)

# Limite padrão para alerta de estoque baixo
LOW_STOCK_THRESHOLD = int(os.environ.get("LOW_STOCK_THRESHOLD", "10"))


def lambda_handler(event, context):
    """
    Ponto de entrada da Lambda.
    O campo 'action' no evento define qual operação será executada.
    """
    logger.info("Evento recebido: %s", json.dumps(event))

    action = event.get("action")

    actions = {
        "put_item":        put_item,
        "get_item":        get_item,
        "list_items":      list_items,
        "check_low_stock": check_low_stock,
    }

    if action not in actions:
        return build_response(400, {
            "error": f"Ação inválida: '{action}'",
            "acoes_validas": list(actions.keys())
        })

    try:
        return actions[action](event)
    except ClientError as e:
        # Erros do SDK da AWS (DynamoDB, KMS, etc.)
        logger.error("Erro AWS: %s", e.response["Error"]["Message"])
        return build_response(500, {"error": "Erro interno AWS", "detalhes": str(e)})
    except Exception as e:
        logger.error("Erro inesperado: %s", str(e))
        return build_response(500, {"error": "Erro interno", "detalhes": str(e)})


def put_item(event):
    """
    Insere ou atualiza um item no inventário.
    Campos obrigatórios: ProductID, ProductName, Quantity
    """
    payload = event.get("payload", {})

    # Validação dos campos obrigatórios
    required_fields = ["ProductID", "ProductName", "Quantity"]
    missing = [f for f in required_fields if f not in payload]
    if missing:
        return build_response(400, {"error": f"Campos obrigatórios ausentes: {missing}"})

    # Timestamp ISO 8601 em UTC — usado como range_key
    updated_at = datetime.now(timezone.utc).isoformat()

    item = {
    "ProductID":   payload["ProductID"],
    "UpdatedAt":   updated_at,
    "ProductName": payload["ProductName"],
    "Quantity":    payload["Quantity"],
    "Category":    payload.get("Category", "Sem categoria"),
    "Size":        payload.get("Size", "U"),        # Tamanho: P, M, G, GG
    "Color":       payload.get("Color", "Único"),   # Cor do produto
    "Unit":        payload.get("Unit", "pç"),       # peça, não "un"
}

    table.put_item(Item=item)

    logger.info("Item gravado: ProductID=%s Quantity=%s",
                item["ProductID"], item["Quantity"])

    return build_response(201, {
        "message": "Item gravado com sucesso",
        "item": item
    })


def get_item(event):
    """
    Busca o item mais recente de um produto pelo ProductID.
    Campo obrigatório: ProductID
    """
    product_id = event.get("ProductID")

    if not product_id:
        return build_response(400, {"error": "Campo 'ProductID' é obrigatório"})

    # Query pelo ProductID, ordenado por UpdatedAt desc — traz o mais recente
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("ProductID").eq(product_id),
        ScanIndexForward=False,  # ordem decrescente (mais recente primeiro)
        Limit=1
    )

    items = response.get("Items", [])
    if not items:
        return build_response(404, {"error": f"Produto '{product_id}' não encontrado"})

    return build_response(200, {"item": items[0]})


def list_items(event):
    """
    Lista todos os itens do inventário (Scan completo).
    Atenção: em tabelas grandes, prefira usar Query com filtros.
    """
    response = table.scan()
    items = response.get("Items", [])

    logger.info("Total de itens encontrados: %d", len(items))

    return build_response(200, {
        "total": len(items),
        "items": items
    })


def check_low_stock(event):
    """
    Verifica itens com estoque abaixo do limite (LOW_STOCK_THRESHOLD).
    Retorna lista de produtos que precisam de reposição.
    """
    response = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr("Quantity").lt(LOW_STOCK_THRESHOLD)
    )

    low_stock_items = response.get("Items", [])

    logger.warning("Itens com estoque baixo: %d (limite: %d)",
                   len(low_stock_items), LOW_STOCK_THRESHOLD)

    return build_response(200, {
        "threshold":       LOW_STOCK_THRESHOLD,
        "total_alertas":   len(low_stock_items),
        "itens_criticos":  low_stock_items
    })


def build_response(status_code, body):
    """Monta resposta padronizada com status HTTP e corpo JSON."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str, ensure_ascii=False)
    }