# VelocidadVenta.py
import os
import json
import boto3

# Variables de entorno (más flexible para dev/prod)
AWS_REGION     = os.getenv("AWS_REGION", "us-east-1")
ENDPOINT_NAME  = os.getenv("ENDPOINT_NAME", "velocidad-venta-lgbm")
CONTENT_TYPE   = os.getenv("CONTENT_TYPE", "application/json")
ACCEPT         = os.getenv("ACCEPT", "application/json")

runtime = boto3.client("sagemaker-runtime", region_name=AWS_REGION)

def _parse_body(event):
    """
    Devuelve el body como objeto Python.
    Soporta API Gateway REST y HTTP API (string JSON) o body ya parseado.
    """
    body = event.get("body", {})
    if isinstance(body, (dict, list)):
        return body
    if body is None:
        return {}
    try:
        return json.loads(body)
    except Exception:
        # También intentamos si viene como url-encoded con "body" JSON dentro
        return {}

def _response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": json.dumps(payload, ensure_ascii=False)
    }

def lambda_handler(event, context):
    """
    Espera:
    - Un solo registro (objeto JSON con tus campos), o
    - Batch: {"registros": [ {...}, {...} ]}  o  {"registro": {...}}
    Devuelve: {"prediccion": [...]} o {"prediccion": valor}
    """
    try:
        payload = _parse_body(event)

        # Determinar si viene batch o single
        if isinstance(payload, dict) and "registros" in payload:
            data = payload["registros"]           # lista de dicts
        elif isinstance(payload, dict) and "registro" in payload:
            data = payload["registro"]            # dict
        else:
            # si el body ES ya el dict con las features, úsalo tal cual
            data = payload

        # Validar forma soportada por tu endpoint (dict o list de dicts)
        if isinstance(data, dict):
            body_to_send = json.dumps(data)
        elif isinstance(data, list):
            body_to_send = json.dumps(data)
        else:
            return _response(400, {
                "error": "El body debe ser un objeto JSON o una lista de objetos."
            })

        # Invocar el endpoint de SageMaker
        sm_response = runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType=CONTENT_TYPE,
            Accept=ACCEPT,
            Body=body_to_send
        )

        raw = sm_response["Body"].read().decode("utf-8")

        # Tu inference.py devuelve JSON; intenta parsearlo
        try:
            pred = json.loads(raw)
        except Exception:
            pred = raw  # en caso el contenedor devuelva texto

        # Uniformar respuesta
        return _response(200, {
            "endpoint": ENDPOINT_NAME,
            "prediccion": pred
        })

    except Exception as e:
        return _response(500, {
            "error": str(e),
            "endpoint": ENDPOINT_NAME
        })
