import asyncio
from asyncio import sleep

import aio_pika
import aio_pika.abc
from aiormq.abc import DeliveredMessage
from pamqp.commands import Basic
from keyboard_alike import reader
from datetime import datetime, timezone

class Publisher:
    connection :aio_pika.RobustConnection
    channel: aio_pika.abc.AbstractChannel

    def __init__(self, host, queue):
        self.connection = None
        self.channel = None
        self.host = host
        self.queue = queue

    async def setup_connection(self):
        loop = asyncio.get_running_loop()
        self.connection = await aio_pika.connect_robust(
            self.host, loop=loop
        )
        self.channel = await self.connection.channel()

    async def publish(self, msg):
        try:
            ack:DeliveredMessage = await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=str(msg).encode()
                ),
                routing_key=self.queue
            )
    
            self.log_result(ack, msg)
        except Exception as e:
            print(f'publish exception {e}')

    async def close(self):
        if self.connection is not None:
            await self.connection.close()

    def log_result(self, ack, msg):
        if isinstance(ack, Basic.Ack):
            print(f'published {msg}')
        else:
            reason = 'unknown'
            if 'delivery' in ack and isinstance(ack.delivery, Basic.Return):
                reason = ack.delivery.reply_text

            print(f'error delivering message {msg}: {reason}')
        pass


def run_publish_task(publisher : Publisher, msg):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(publisher.publish(msg))

    except Exception as e:
        print(e)
    pass



async def main(msg):
	publisher = Publisher(f"amqp://admin:admin@localhost:11000/","card-scans")
	await publisher.setup_connection()
	await publisher.publish(msg)
	await publisher.close()
if __name__ == '__main__':
    #now = datetime.now().replace(microsecond=0, tzinfo=timezone.utc).isoformat()
    cursor = reader.Reader(0xffff, 53, 8, 16, should_reset=False)
    cursor.initialize()
    while True:
        now = datetime.now().replace(microsecond=0, tzinfo=timezone.utc).isoformat()
        msg = cursor.read().strip()
        l=len(msg)
        if l>4:
            msg=msg[-4:]
            asyncio.run(main('{"cardId": "'+msg+'", "readerId": "53", "timestamp": "'+now+'"}'))
        else
            continue
    cursor.disconnect()
