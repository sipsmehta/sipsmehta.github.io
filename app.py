from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
import logging
import os
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

app = FastAPI()

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    # Add other origins here if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

# Set up the conversation memory
memory = ConversationBufferWindowMemory(k=3, return_messages=True)

@app.get("/chat")
async def chat(api_key: str = Query(...), prompt: str = Query(...), history: Optional[List[str]] = Query([])):
    logging.info(f"Received api_key: {api_key}")
    logging.info(f"Received prompt: {prompt}")
    logging.info(f"Received history: {history}")
    try:
        history_messages = [json.loads(msg) for msg in history]
        logging.info(f"Parsed history: {history_messages}")
    except Exception as e:
        logging.error(f"Error parsing history: {e}")
        return {"error": "Error parsing history"}

    # Initialize the conversation if not already done
    if not hasattr(app.state, 'conversation'):
        try:
            llm = ChatOpenAI(
                model="accounts/fireworks/models/llama-v3p1-405b-instruct",
                openai_api_key=api_key, 
                openai_api_base="https://api.fireworks.ai/inference/v1"
            )
            app.state.conversation = ConversationChain(
                memory=memory, 
                llm=llm
            )
        except Exception as e:
            logging.error(f"Error initializing conversation: {e}")
            return {"error": "Error initializing conversation"}

    # Process the conversation
    try:
        response = app.state.conversation.predict(input=prompt)
    except Exception as e:
        logging.error(f"Error during conversation: {e}")
        return {"error": "Error during conversation"}

    return {"response": response}
