from fastapi import APIRouter, Request, Query
from fastapi.responses import PlainTextResponse

router = APIRouter(
    prefix="/api/whatsapp",
    tags=["WhatsApp"]
)

# Temporary verification token.
# We will later move this into your .env file.
VERIFY_TOKEN = "devera_whatsapp_verify"


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if (
        hub_mode == "subscribe"
        and hub_verify_token == VERIFY_TOKEN
    ):
        return PlainTextResponse(content=hub_challenge)

    return PlainTextResponse(
        content="Verification failed",
        status_code=403
    )


@router.post("/webhook")
async def receive_whatsapp_webhook(request: Request):
    data = await request.json()

    print("WHATSAPP WEBHOOK RECEIVED:")
    print(data)

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        messages = value.get("messages", [])

        if not messages:
            return {"status": "received"}

        message = messages[0]

        sender = message["from"]
        message_type = message.get("type")

        if message_type == "text":
            question = message["text"]["body"]

            print("SENDER:", sender)
            print("MESSAGE:", question)

            # For now, just test that we extracted it.
            return {
                "status": "received",
                "sender": sender,
                "question": question
            }

        return {
            "status": "received",
            "message": "Unsupported message type"
        }

    except (KeyError, IndexError, TypeError):
        return {
            "status": "received",
            "message": "Webhook received, but message structure was not recognized"
        }
    
