import os
from openai import AzureOpenAI

endpoint = "https://yoges-mdbraw1t-eastus2.cognitiveservices.azure.com/"
model_name = "gpt-5-mini"
deployment = "gpt-5-mini"

subscription_key = "2vmiQacLtF35eltzROIOOZ6P37AQNz07tWqDawwRa5qhQY25z8iwJQQJ99BGACHYHv6XJ3w3AAAAACOGylfG"
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "I am going to Paris, what should I see?",
        }
    ],
    model=deployment
)

print(response.choices[0].message.content)
