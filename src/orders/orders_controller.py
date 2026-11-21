import json
from decimal import Decimal

from flask import Blueprint, current_app, jsonify, request

from .dto.create_order_dto import ValidationError, parse_create_order
from .orders_service import OrderLimitError

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


def _error(status: int, message, error: str):
    response = jsonify({"statusCode": status, "message": message, "error": error})
    response.status_code = status
    return response


@orders_bp.post("")
def create_order():
    try:
        # parse_float=Decimal conserva los decimales exactos del precio.
        body = json.loads(request.get_data(), parse_float=Decimal)
    except (ValueError, UnicodeDecodeError):
        return _error(400, "Malformed JSON body", "Bad Request")

    try:
        order = parse_create_order(body)
        result = current_app.extensions["orders_service"].create(order)
    except ValidationError as exc:
        return _error(400, exc.messages, "Bad Request")
    except OrderLimitError as exc:
        return _error(400, str(exc), "Bad Request")

    return jsonify(result), 201
