import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from ai_utils.config_loader import load_few_shot_examples


example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"), 
            ("ai", "{output}"),
        ]
    )

def process_image(img):
    vision_model = ChatGoogleGenerativeAI(model="gemini-pro-vision", stream=True, convert_system_message_to_human=True)

    # Create multimodal prompt with PIL image
    multimodal_prompt = HumanMessage(
        content=[
            {"type": "text", "text": "List all the food items on this receipt, including their prices in a comma separated list."},
            {"inline_data": img}
        ]
    )

    image_prompt_template = ChatPromptTemplate.from_messages([multimodal_prompt])
    chain = (
        image_prompt_template
        | vision_model
        | StrOutputParser()
    )

    output = chain.invoke({})
    return output

def filter_list(raw_text: str) -> str:
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

    result = text_model.invoke("Remove all non food items and their prices from the list. DO NOT ADD ANY ADDITIONAL TEXT. \n" + raw_text)

    return result.content

def create_raw_json(raw_text: str) -> str:
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

    few_shot_examples = load_few_shot_examples('configs/few_shot_examples.json')

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=few_shot_examples,
    )

    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Convert the provided lists to JSON. Only return JSON. DO NOT ADD ANY ADDITIONAL TEXT."),
                few_shot_prompt,
                ("human", raw_text)
            ] 
        )
    
    chain = (
        prompt
        | text_model
        | StrOutputParser()
    )

    output = chain.invoke({})
    return output



def enrich_json(data_raw_json: str) -> str:
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

    result = text_model.invoke("Enrich each item in the JSON with a nutritional value from 0 to 10. DO NOT ADD ANY ADDITIONAL TEXT. \n" + data_raw_json)

    return result.content