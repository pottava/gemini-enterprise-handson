import requests

BASE_URL = "https://fakestoreapi.com"


def get_all_products(limit: int = 0, sort: str = "") -> dict:
    """全商品一覧を取得します。

    Args:
        limit: 取得件数の上限（0 は全件）。
        sort: 並び順。"asc"（昇順）または "desc"（降順）。
    """
    params = {}
    if limit > 0:
        params["limit"] = limit
    if sort in ("asc", "desc"):
        params["sort"] = sort
    resp = requests.get(f"{BASE_URL}/products", params=params)
    if not resp.ok:
        return {"status": "error", "message": resp.text}
    return {"status": "success", "result": resp.json()}


def get_product(product_id: int) -> dict:
    """指定した ID の商品詳細を取得します。

    Args:
        product_id: 商品 ID。
    """
    resp = requests.get(f"{BASE_URL}/products/{product_id}")
    if not resp.ok:
        return {"status": "error", "message": resp.text}
    return {"status": "success", "result": resp.json()}


def get_product_categories() -> dict:
    """商品カテゴリー一覧を取得します。"""
    resp = requests.get(f"{BASE_URL}/products/categories")
    if not resp.ok:
        return {"status": "error", "message": resp.text}
    return {"status": "success", "result": resp.json()}


def get_products_by_category(category: str, limit: int = 0, sort: str = "") -> dict:
    """指定したカテゴリーの商品一覧を取得します。

    Args:
        category: カテゴリー名（例: "electronics", "jewelery", "men's clothing", "women's clothing"）。
        limit: 取得件数の上限（0 は全件）。
        sort: 並び順。"asc"（昇順）または "desc"（降順）。
    """
    params = {}
    if limit > 0:
        params["limit"] = limit
    if sort in ("asc", "desc"):
        params["sort"] = sort
    resp = requests.get(f"{BASE_URL}/products/category/{category}", params=params)
    if not resp.ok:
        return {"status": "error", "message": resp.text}
    return {"status": "success", "result": resp.json()}
