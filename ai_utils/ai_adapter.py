import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.messages import HumanMessage
from langchain.schema import StrOutputParser
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate, PromptTemplate
from ai_utils.config_loader import load_few_shot_examples
from pydantic import ValidationError, BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from typing import List


example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"), 
            ("ai", "{output}"),
        ]
    )


# Pydantic models for data validation
class ReceiptItem(BaseModel):
    itemName: str = Field(description="Name of the item")
    price: float = Field(description="Price of the item")

class Receipt(BaseModel):
    receiptItems: List[ReceiptItem] = Field(description="List of receipt items")

class EnrichedReceiptItem(BaseModel):
    itemName: str = Field(description="Name of the item")
    price: float = Field(description="Price of the item")
    nutritionalValue: int = Field(0, description="Nutritional value of the item from 0 to 10")

class EnrichedReceipt(BaseModel):
    receiptItems: List[EnrichedReceiptItem] = Field(description="List of receipt items with nutritional values")

class SuggestionItem(BaseModel):
    prevItem: str = Field(description="Name of the previous item")
    prevItemPrice: float = Field(description="Price of the previous item")
    newItem: str = Field(description="Name of the new item")
    newItemPrice: float = Field(description="Price of the new item")
    description: str = Field(description="One sentence explanation of the suggestion")

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

def process_url(image_url: str):
    vision_model = ChatGoogleGenerativeAI(model="gemini-pro-vision", stream=True, convert_system_message_to_human=True)

    # Create multimodal prompt with PIL image
    multimodal_prompt = HumanMessage(
        content=[
            {"type": "text", "text": "List all the food items on this receipt, including their prices in a comma separated list."},
            {"type": "image_url", "image_url": image_url}
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

    # Potentially use a few-shot prompt to help the model understand the task
    few_shot_examples = load_few_shot_examples('configs/few_shot_examples.json')
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=few_shot_examples,
    )

    parser = PydanticOutputParser(pydantic_object=Receipt)

    prompt = PromptTemplate(
        template="Convert the provided list to JSON.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | text_model | parser

    try:
        validated_data = chain.invoke({"query": raw_text})
        return json.dumps(validated_data.dict())
    except Exception as e:
        return f"Error: {e}"



def add_nutritional_data(data_raw_json: str) -> str:
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

    result = text_model.invoke("Enrich each item in the JSON with a nutritional value from 0 to 10.\n" + data_raw_json)

    try:
        parsed_output = json.loads(result.content)
        validated_data = EnrichedReceipt(**parsed_output)
        return validated_data.model_dump_json()
    except json.JSONDecodeError:
        return "Error: The output is not valid JSON." + result.content
    except ValidationError as e:
        return f"Validation error: {e}"
    

def get_suggestions(items: str) -> str:
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

    parser = PydanticOutputParser(pydantic_object=SuggestionItem)

    prompt = PromptTemplate(
        template="Suggest a healthier alternative in the same price range.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | text_model | parser

    try:
        validated_data = chain.invoke({"query": items})
        return json.dumps(validated_data.dict())
    except Exception as e:
        return f"Error: {e}"
