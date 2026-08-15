import pytchat
import json

chat = pytchat.create(video_id="3Y-5L7XCJ94")
all_chat_data = []

while chat.is_alive():
    # .items fetches the data in bulk chunks immediately
    for c in chat.get().items: 
        msg_data = {
            "datetime": c.datetime,
            "author": c.author.name,
            "message": c.message,
            "amount": c.amountValue,
            "currency": c.currency,
            "type": c.type
        }
        all_chat_data.append(msg_data)

with open('raw_transactions.json', 'w', encoding='utf-8') as f:
    json.dump(all_chat_data, f, indent=4)