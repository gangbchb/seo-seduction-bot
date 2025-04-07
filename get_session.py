from pyrogram import Client

api_id = "20717939"
api_hash = "323eb4d6cb37805bab1a41a68768a839"

app = Client("seo_seduction_bot", api_id=api_id, api_hash=api_hash)

with app:
    session_string = app.export_session_string()
    print("Your session string:")
    print(session_string)