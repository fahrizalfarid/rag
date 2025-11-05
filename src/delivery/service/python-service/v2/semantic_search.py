import asyncio
import json
import nats
from src.llm_rag import LLM

async def main():
    try:
        nc = await nats.connect("nats://127.0.0.1:4222")
        llm = LLM(
            dbpath="/path/code/src/delivery/service/python-service/v2/milvus_law_qa_semantic.db",
        )
        
        async def message_handler(msg):
            subject = msg.subject
            reply = msg.reply
            data = json.loads(msg.data)
            print("Received a message on '{subject} {reply}': {data}".format(
                subject=subject, reply=reply, data=data["query"]))
            
            if msg.reply:
                response_payload = llm.Forward(data["query"], data["vector"], True, data["k"])
                print(response_payload)
                await nc.publish(msg.reply, json.dumps({
                    "content":response_payload
                }).encode('utf-8'))

        await nc.subscribe("llm/semantic_search", cb=message_handler)
        while True:
            await asyncio.sleep(1)

    except nats.errors.NoServersError:
        print("nats error")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("interrupted")
