import aiohttp
import config


async def add_user(tg_token, tg_chat_id):
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{config.server_ip}/api/v1/users/get_by_token/?remember_token={str(tg_token)}&tg_chat_id={str(tg_chat_id)}"
            response = await session.get(url, headers={'Authorization': f'{config.auth_api_token}'})
        except ExceptionGroup:
            return None
        return response


async def get_user_data(website_id):
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{config.server_ip}/api/v1/users/{str(website_id)}"
            response = await session.get(url, headers={'Authorization': f'{config.auth_api_token}'})
        except ExceptionGroup:
            return None
        return response


async def get_user_by_mail(email):
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{config.server_ip}/api/v1/users/get_by_email/?email={str(email)}"
            response = await session.get(url, headers={'Authorization': f'{config.auth_api_token}'})
        except ExceptionGroup:
            return None
        return response


async def get_users_data():
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{config.server_ip}/api/v1/users"
            response = await session.get(url, headers={'Authorization': f'{config.auth_api_token}'})
        except ExceptionGroup:
            return None
        return response


async def questions_data():
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{config.server_ip}/api/v1/submit"
            response = await session.get(url, headers={'Authorization': f'{config.auth_api_token}'})
        except ExceptionGroup:
            return None
        return response


async def question_data(question_id):
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{config.server_ip}/api/v1/submit/{question_id}"
            response = await session.get(url, headers={'Authorization': f'{config.auth_api_token}'})
        except ExceptionGroup:
            return None
        return response


async def questionForm_solved(question_id):
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{config.server_ip}/api/v1/submit/{question_id}/solve/"
            response = await session.post(url, headers={'Authorization': f'{config.auth_api_token}'})
        except ExceptionGroup:
            return None
        return response
