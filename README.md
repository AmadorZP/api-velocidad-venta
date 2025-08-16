# API Velocidad de Venta (Serverless + SageMaker)

Este servicio expone un modelo ya entrenado a través de un endpoint HTTP. En SageMaker se empaquetaron los artefactos (`modelo_velocidad_venta.joblib`, `model_columns.joblib`, `categorical_info.joblib`) y se desplegó un endpoint usando **SKLearnModel** con la imagen oficial de Scikit-learn. El `entry_point` de inferencia maneja la carga del modelo, el parseo de **JSON**, el preprocesamiento (orden de columnas y categorías) y respuesta en **JSON**.

Para disponibilizarlo, se implementó un microservicio en **AWS Lambda** detrás de **API Gateway**. `VelocidadVenta.py` actúa como *handler*: lee el cuerpo de la solicitud (objeto o lista), invoca `sagemaker-runtime:InvokeEndpoint` al endpoint identificado por la variable de entorno `ENDPOINT_NAME` y devuelve una respuesta JSON. `serverless.yml` define el runtime (Python 3.13), región, rol IAM existente y el evento `POST /predecir/velocidad-venta`.

---

## Archivos
- **VelocidadVenta.py**: Lambda handler que invoca el endpoint de SageMaker.
- **serverless.yml**: Infraestructura y configuración del endpoint HTTP (API Gateway + Lambda).

## Despliegue
```bash
serverless deploy
```

## Prueba rápida (Postman o curl)
**POST** `https://<api-id>.execute-api.<region>.amazonaws.com/dev/predecir/velocidad-venta`  
Header: `Content-Type: application/json`  
Body (ejemplo, un registro):
```json
{
  "Inmobiliaria": "Inmobiliaria_5",
  "Tipología": "TIPO A",
  "Distrito": "Ate",
  "Fase_de_Proyecto": "En Planos",
  "Ratio_Cocheras": 1.5,
  "Cantidad_de_Unidades_Totales": 120,
  "Latitud": -12.12,
  "Longitud": -77.03,
  "Cantidad_Total_de_Estacionamientos": 180,
  "Cantidad_de_Depósitos": 100,
  "Id_Inmobiliaria": 5,
  "Cantidad_de_Pisos": 15,
  "Precio_de_Lista": 250000
}

```
**Respuesta Postman (ejemplo):**
```json
{
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    },
    "body": "{\"endpoint\": \"velocidad-venta-lgbm\", \"prediccion\": [0.027462408450716774]}"
}
```
