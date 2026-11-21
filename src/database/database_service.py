import os

from psycopg_pool import ConnectionPool


def _read_port() -> int:
    try:
        port = int(os.environ.get("DB_PORT", "5432"))
    except ValueError:
        port = 0
    if not 1 <= port <= 65535:
        raise ValueError("DB_PORT must be an integer between 1 and 65535")
    return port


class DatabaseService:
    """Pool de conexiones a PostgreSQL (equivalente al DatabaseService de Nest)."""

    def __init__(self) -> None:
        conninfo = (
            f"host={os.environ.get('DB_HOST', 'localhost')} "
            f"port={_read_port()} "
            f"user={os.environ.get('DB_USER', 'postgres')} "
            f"password={os.environ.get('DB_PASSWORD', 'postgres')} "
            f"dbname={os.environ.get('DB_NAME', 'orders_db')}"
        )
        self.pool = ConnectionPool(
            conninfo,
            min_size=int(os.environ.get("DB_POOL_MIN", "2")),
            max_size=int(os.environ.get("DB_POOL_MAX", "10")),
            timeout=5,  # equivalente a connectionTimeoutMillis: 5000
            open=False,
        )
        self.pool.open()

    def connection(self):
        """Devuelve un context manager: BEGIN/COMMIT, o ROLLBACK si hay error."""
        return self.pool.connection()

    def close(self) -> None:
        self.pool.close()
