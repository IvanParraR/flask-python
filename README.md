# Orders API

Microservicio de órdenes implementado con Python, Flask y PostgreSQL para el
taller de benchmarking con JMeter.

## Requisitos

- Python 3.12+ y pip
- Docker con Docker Compose
- Apache JMeter (para ejecutar las pruebas)

## Ejecutar con Docker Compose

```bash
docker compose up --build -d
docker compose ps
```

La API queda disponible en `http://localhost:5001` y PostgreSQL en el puerto
`5433` del host. El esquema se crea al iniciar la base de datos por primera
vez. La API corre con Gunicorn (4 workers x 8 hilos).

## Ejecutar localmente

Arranca PostgreSQL (por ejemplo, con `docker compose up -d db`) y ejecuta:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DB_PORT=5433 python -m src.main
```

La aplicación lee `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`,
`PORT`, `DB_POOL_MIN` y `DB_POOL_MAX`. Los valores predeterminados son
`localhost`, `5432`, `postgres`, `postgres`, `orders_db`, `5001`, `2` y `10`.

## Crear una orden

`POST /api/orders`:

```json
{
  "customerId": "C123",
  "items": [
    { "productId": "P1", "quantity": 2, "price": 10.5 },
    { "productId": "P2", "quantity": 1, "price": 5.0 }
  ]
}
```

Respuesta (`201 Created`):

```json
{
  "orderId": "d6ad70e0-8d16-4f38-86ad-39c88d14660d",
  "totalAmount": 26.0,
  "itemsCount": 3,
  "processedAt": "2026-11-20T00:00:00.000Z"
}
```

`itemsCount` es la suma de las cantidades. Los importes se calculan y guardan
con precisión de centavos. Las escrituras en `orders` y `order_items` se hacen
en una transacción.

Ejemplo con `curl`:

```bash
curl -i http://localhost:5001/api/orders \
  -H 'Content-Type: application/json' \
  -d '{"customerId":"C123","items":[{"productId":"P1","quantity":2,"price":10.5},{"productId":"P2","quantity":1,"price":5}]}'
```

La API rechaza órdenes vacías, tipos inválidos y propiedades no declaradas.
