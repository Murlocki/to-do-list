import httpx
from fastapi import HTTPException

async def proxy_request(external_url: str, method: str, headers: dict, data: dict = None):
    try:
        async with httpx.AsyncClient() as client:
            # Проксируем запрос к внешнему сервису
            if method.lower() == "get":
                response = await client.get(external_url, headers=headers, params=data)
            elif method.lower() == "post":
                response = await client.post(external_url, headers=headers, json=data)
            elif method.lower() == "put":
                response = await client.put(external_url, headers=headers, json=data)
            elif method.lower() == "patch":
                response = await client.patch(external_url, headers=headers, json=data)
            elif method.lower() == "delete":
                response = await client.delete(external_url, headers=headers)
            else:
                raise HTTPException(status_code=400, detail="Invalid HTTP method")

            # Возвращаем ответ от внешнего сервиса
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": await response.json()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    async def get_all_users():
        headers = {
        "content-type": "application/json",
    }
        users = await proxy_request(f"{settings.profile_service_url}/user","GET",headers=headers)
    return users