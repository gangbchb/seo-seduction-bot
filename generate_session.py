from pyrogram import Client

api_id = "20717939"  # Замени на свой PYROGRAM_API_ID
api_hash = "323eb4d6cb37805bab1a41a68768a839"  # Замени на свой PYROGRAM_API_HASH

app = Client("my_session", api_id=api_id, api_hash=api_hash)

with app:
    session_string = app.export_session_string()
    print("Session string:", session_string)