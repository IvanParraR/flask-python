import atexit
import os

from flask import Flask

from .database.database_service import DatabaseService
from .orders.orders_controller import orders_bp
from .orders.orders_service import OrdersService


def create_app() -> Flask:
    app = Flask(__name__)
    app.json.sort_keys = False

    database = DatabaseService()
    atexit.register(database.close)
    app.extensions["orders_service"] = OrdersService(database)

    # Prefijo global 'api' -> POST /api/orders
    app.register_blueprint(orders_bp, url_prefix="/api/orders")

    @app.errorhandler(404)
    def not_found(_):
        return {"statusCode": 404, "message": "Not Found", "error": "Not Found"}, 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return {
            "statusCode": 405,
            "message": "Method Not Allowed",
            "error": "Method Not Allowed",
        }, 405

    @app.errorhandler(Exception)
    def internal_error(exc):
        app.logger.exception("Unhandled error", exc_info=exc)
        return {
            "statusCode": 500,
            "message": "Internal server error",
            "error": "Internal Server Error",
        }, 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5001")))
