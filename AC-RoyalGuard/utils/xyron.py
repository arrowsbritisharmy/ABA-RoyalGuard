import json
import aiohttp
from decouple import config

async def send_request(url, body=None):
	headers = {
		'Auth': config('XYLON_AUTH'),
		'Content-Type': 'application/json',
	}
	method = 'POST' if body else 'GET'
	data = json.dumps(body) if body else None
	async with aiohttp.ClientSession() as session:
		async with session.request(method=method, url=config('XYLON_API') + url, headers=headers, data=data) as response:
			return await response.json()