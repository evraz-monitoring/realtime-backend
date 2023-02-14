import asyncio
import json
import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect
from redis.asyncio.client import Redis

import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/metrics");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    redis = Redis.from_url(settings.REDIS_URL)
    done, pending = await asyncio.wait(
        [chatroom_ws_sender(websocket, redis), chatroom_ws_receiver(websocket, redis)],
        return_when=asyncio.FIRST_COMPLETED,
    )
    logger.debug(f"Done task: {done}")
    for task in pending:
        logger.debug(f"Canceling task: {task}")
        task.cancel()
    await redis.close()


async def chatroom_ws_receiver(ws: WebSocket, r: Redis):
    try:
        while True:
            message = await ws.receive_text()
            if message:
                await r.publish(settings.METRICS_STREAM, message)
                logger.debug("RECEIVE FROM CLIENT %s", message.encode("utf-8"))
    except WebSocketDisconnect as exc:
        # TODO this needs handling better
        logger.error(exc)


async def chatroom_ws_sender(ws: WebSocket, r: Redis):
    p = r.pubsub()
    await p.subscribe(settings.METRICS_STREAM)
    try:
        while True:
            message = await p.get_message(ignore_subscribe_messages=True)
            if message:
                logger.debug("RECEIVE FROM REDIS %s", message)
                message = message["data"].decode("utf-8")
                await ws.send_json(json.loads(message))
    except Exception as exc:
        # TODO this needs handling better
        logger.error(exc)