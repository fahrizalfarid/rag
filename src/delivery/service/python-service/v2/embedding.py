import asyncio
import json
import nats
from src.llm_embeddings import LLMEmbeddings

async def main():
    try:
        nc = await nats.connect("nats://127.0.0.1:4222")
        llm = LLMEmbeddings()
        
        async def message_handler(msg):
            subject = msg.subject
            reply = msg.reply
            data = json.loads(msg.data)
            print("Received a message on '{subject} {reply}': {data}".format(
                subject=subject, reply=reply, data=data['content']))
            
            if msg.reply:
                response_payload = llm.get_embeddings(data['content'])
                await nc.publish(msg.reply, json.dumps({
                    "query":data['content'],
                    "vector":response_payload,
                }).encode('utf-8'))

        await nc.subscribe("llm/embedding", cb=message_handler)
        while True:
            await asyncio.sleep(1)

    except nats.errors.NoServersError:
        print("nats error")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("interrupted")
