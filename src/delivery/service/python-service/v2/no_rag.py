import asyncio
import json
import nats
import requests



async def generate_response(prompt):
    payload = {
        "prompt":prompt,
        "n_predict":256, # max token
        # "temperatur":0.7,
        "stop": ["\nUser:", "<|end_of_text|>", "User:", "###"],
    }
    try:
        res = requests.post('http://localhost:8081/completion', json=payload, timeout=60*10)
        answer = res.json()['content']
        return answer.strip()
    except Exception as e:
        return "LLM was not respond."

async def main():
    try:
        nc = await nats.connect("nats://127.0.0.1:4222")
        
        async def message_handler(msg):
            subject = msg.subject
            reply = msg.reply
            data = json.loads(msg.data)
            print("Received a message on '{subject} {reply}': {data}".format(
                subject=subject, reply=reply, data=data))
            
            if msg.reply:
                response_payload = await generate_response(data['content'][0])
                await nc.publish(msg.reply, json.dumps({
                    "content":[response_payload]
                }).encode('utf-8'))

        await nc.subscribe("llm/completion/no_rag", cb=message_handler)
        while True:
            await asyncio.sleep(1)

    except nats.errors.NoServersError:
        print("nats error")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("interrupted")
