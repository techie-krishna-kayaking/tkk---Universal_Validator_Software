from fastapi import Request


def client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def geo_country(request: Request) -> str | None:
    return request.headers.get("X-Geo-Country")


def user_agent(request: Request) -> str | None:
    return request.headers.get("User-Agent")
