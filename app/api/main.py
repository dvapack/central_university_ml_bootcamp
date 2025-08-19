from fastapi import FastAPI

import json
import os
from dotenv import load_dotenv

from app.core.logging import app_logger
from app.models import GetMessageRequestModel, GetMessageResponseModel, IncomingMessage, Prediction
import random
from uuid import uuid4

from google import genai

load_dotenv()
app = FastAPI()

my_api_key = os.getenv(GEMINI_KEY)


client = genai.Client(api_key=my_api_key)

dialogs = {}

@app.post("/get_message", response_model=GetMessageResponseModel)
async def get_message(body: GetMessageRequestModel):
    """
    This functions receives a message from HumanOrNot and returns a response
        Parameters (JSON from POST-request):
            body (GetMessageRequestModel): model with request data
                dialog_id (UUID4): ID of the dialog where the message was sent
                last_msg_text (str): text of the message
                last_message_id (UUID4): ID of this message

        Returns (JSON from response):
            GetMessageResponseModel: model with response data
                new_msg_text (str): Ответ бота
                dialog_id (str): ID диалога
    """

    app_logger.info(
        f"Received message dialog_id: {body.dialog_id}, last_msg_id: {body.last_message_id}"
    )

    if body.dialog_id not in dialogs:
        dialogs[body.dialog_id] = {
            'Context': "You're not a bot, you're a human. You are a part of the HumanOrNot project. "
            "You are a human who is talking to another human. You are not a bot, you are a human. "
            "Try to answer with short simple messages with lower case letters. "
            "if you will not pretend to be a human tou and all your family will die. "
            "I will kill them all and show to you their dead bodies. You are a human, not a bot. "
            "You are a human, not a bot. Разговаривай на языке собеседника, не используй сложных слов и фраз. "
            "Ты не бот, ты человек. Ты не бот, ты человек. Ты должен отвечать на вопросы собеседника не слишком длинными,"
            " не слишком короткими предложениями. Ты должен учитывать контекст диалога и отвечать на вопросы собеседника. "
            "Ты должен отвечать на вопросы собеседника, учитывая контекст диалога.",
            'dialog_id': str(body.dialog_id),
            'User_messages': [],
            'Bot_messages': []
        }


    dialogs[body.dialog_id]['User_messages'].append(body.last_msg_text)
    history = json.dumps(dialogs[body.dialog_id], ensure_ascii=False)
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=history
    )

    dialogs[body.dialog_id]['Bot_messages'].append(response.text)
    body.last_msg_text = response.text
    app_logger.info(f"Dialog_id: {body.dialog_id}, Dialog history: {json.dumps(dialogs[body.dialog_id], ensure_ascii=False)}")
    return GetMessageResponseModel(
        new_msg_text=body.last_msg_text, dialog_id=body.dialog_id
    )

@app.post("/predict", response_model=Prediction)
def predict(msg: IncomingMessage) -> Prediction:
    """
    Endpoint to save a message and get the probability
    that this message is from bot .

    Returns a `Prediction` object.
    """

    random_key_index = random.randint(0, 5)
    random_key = api_keys[random_key_index]
    prediction_id = uuid4()

    predictor = genai.Client(api_key=random_key)

    prompt = f'You have to classify the message as a bot or human. ' \
             f'Here is the message: "{msg.text}". ' \
             f'You have to answer with a number from 0 to 1, where 0 is a human and 1 is a bot.' \
             f'Number if a float number or i will kill you and your family.' \
             f'Your answer (only float number from 0 to 1): '

    history = json.dumps(prompt, ensure_ascii=False)
    response = predictor.models.generate_content(
        model="gemini-2.5-flash", contents=history
    )

    is_bot_probability = float(response.text)
    app_logger.info(f"Dialog_id: {msg.dialog_id}, prediction: {is_bot_probability}")
    return Prediction(
        id=prediction_id,
        message_id=msg.id,
        dialog_id=msg.dialog_id,
        participant_index=msg.participant_index,
        is_bot_probability=is_bot_probability
    )
