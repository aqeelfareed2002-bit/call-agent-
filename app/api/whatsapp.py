import os
import json
import urllib.request
import urllib.error

from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.retrieval.pipeline import answer_question


router = APIRouter(
    prefix="/api/whatsapp",
    tags=["WhatsApp"]
)


# ==========================================
# WhatsApp Configuration
# ==========================================

VERIFY_TOKEN = os.getenv(
    "WHATSAPP_VERIFY_TOKEN",
    "devera_whatsapp_verify"
)

WHATSAPP_ACCESS_TOKEN = os.getenv(
    "WHATSAPP_ACCESS_TOKEN"
)

WHATSAPP_PHONE_NUMBER_ID = os.getenv(
    "WHATSAPP_PHONE_NUMBER_ID"
)

WHATSAPP_API_VERSION = os.getenv(
    "WHATSAPP_API_VERSION"
)


# ==========================================
# Meta Webhook Verification
# ==========================================

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
        return PlainTextResponse(
            content=hub_challenge
        )

    return PlainTextResponse(
        content="Verification failed",
        status_code=403
    )


# ==========================================
# Send WhatsApp Message
# ==========================================

def send_whatsapp_message(
    recipient: str,
    message: str
):
    if not WHATSAPP_ACCESS_TOKEN:
        raise RuntimeError(
            "WHATSAPP_ACCESS_TOKEN is not set"
        )

    if not WHATSAPP_PHONE_NUMBER_ID:
        raise RuntimeError(
            "WHATSAPP_PHONE_NUMBER_ID is not set"
        )

    if not WHATSAPP_API_VERSION:
        raise RuntimeError(
            "WHATSAPP_API_VERSION is not set"
        )

    url = (
        f"https://graph.facebook.com/"
        f"{WHATSAPP_API_VERSION}/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
    )

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "body": message
        }
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": (
                f"Bearer {WHATSAPP_ACCESS_TOKEN}"
            ),
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            response_body = (
                response
                .read()
                .decode("utf-8")
            )

            print("WHATSAPP API RESPONSE:")
            print(response_body)

            return json.loads(response_body)

    except urllib.error.HTTPError as error:

        error_body = (
            error
            .read()
            .decode("utf-8")
        )

        print("WHATSAPP API ERROR:")
        print(error.code)
        print(error_body)

        raise RuntimeError(
            f"WhatsApp API returned HTTP "
            f"{error.code}: {error_body}"
        )

    except urllib.error.URLError as error:

        print("WHATSAPP NETWORK ERROR:")
        print(error)

        raise RuntimeError(
            f"Could not connect to WhatsApp API: {error}"
        )


# ==========================================
# Receive WhatsApp Webhook
# ==========================================

@router.post("/webhook")
async def receive_whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    data = await request.json()

    print("WHATSAPP WEBHOOK RECEIVED:")
    print(data)

    try:

        # ----------------------------------
        # Extract webhook data
        # ----------------------------------

        entry = data.get("entry", [])

        if not entry:
            return {
                "status": "received"
            }

        changes = entry[0].get(
            "changes",
            []
        )

        if not changes:
            return {
                "status": "received"
            }

        value = changes[0].get(
            "value",
            {}
        )

        messages = value.get(
            "messages",
            []
        )

        # ----------------------------------
        # Ignore events without messages
        # ----------------------------------

        if not messages:
            return {
                "status": "received"
            }

        message = messages[0]

        # ----------------------------------
        # Get sender
        # ----------------------------------

        sender = message.get("from")

        # ----------------------------------
        # Get message type
        # ----------------------------------

        message_type = message.get("type")

        print("SENDER:", sender)
        print("MESSAGE TYPE:", message_type)

        # ----------------------------------
        # Currently support text messages
        # ----------------------------------

        if message_type != "text":
            return {
                "status": "received",
                "message": "Unsupported message type"
            }

        # ----------------------------------
        # Extract question
        # ----------------------------------

        question = message.get(
            "text",
            {}
        ).get(
            "body"
        )

        if not sender:
            return {
                "status": "received",
                "message": "Sender not found"
            }

        if not question:
            return {
                "status": "received",
                "message": "Message text not found"
            }

        print("QUESTION:")
        print(question)

        # ==================================
        # Run RAG Pipeline
        # ==================================

        answer = answer_question(
            db=db,
            question=question,
            top_k=5
        )

        print("RAG ANSWER:")
        print(answer)

        # ==================================
        # Send Answer to WhatsApp
        # ==================================

        whatsapp_response = send_whatsapp_message(
            recipient=sender,
            message=answer
        )

        print("WHATSAPP SEND RESPONSE:")
        print(whatsapp_response)

        return {
            "status": "processed"
        }

    except Exception as error:

        print("WHATSAPP WEBHOOK ERROR:")
        print(error)

        return {
            "status": "error",
            "message": str(error)
        }
