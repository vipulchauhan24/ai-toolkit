def find_sql(order_id: str) -> str:
    return "select id, status from orders where id = '" + order_id + "'"
