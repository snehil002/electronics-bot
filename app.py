import openai
import gradio as gr
import time
import os
import json

openai.api_key = os.environ["OPENAI_API_KEY"]

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return response.choices[0]["message"]["content"] #, response.usage#, response.usage["prompt_tokens"], response.usage["completion_tokens"], response.usage["total_tokens"]

def create_chat_str(chat_hist_ui):
    chat_str = ""
    for h in chat_hist_ui:
        usermsg, assmsg = h
        chat_str += f"Human: {usermsg}\n"
        chat_str += f"Assistant: {assmsg}\n"
    return chat_str

# Create a standalone question
def create_standalone_question(user_input, chat_history_str):
    user_message_1 = f"""
You will be provided with a Chat history and a follow up question.
Rephrase the follow up question to be a stand alone question from \
the perspective of a customer.

Chat history:
{chat_history_str}

Follow up question:
{user_input}

Standalone question:
"""
    # print(user_message_1)
    messages = [
        {"role": "user", "content": user_message_1}
    ]
    answer = get_completion_from_messages(messages)
    print("standalone: ", answer)
    return answer

def get_category_and_products_from_user_input(user_input):
    delimiter = "####"
    system_message = f"""
You will be provided with customer service queries. \
The customer service query will be delimited with \
{delimiter} characters.
Output a python list of objects, where each object has \
the following format:
    'category': <one of smartphones, laptops, air_conditioners>,
OR
    'products': <a list of products that must \
    be found in the allowed products below>

Where the categories and products must be found in \
the customer service query.
If a product is mentioned, it must be associated with \
the correct category in the allowed products list below.
If no products or categories are found, output an \
empty list.

Allowed products: 

smartphones category:
iPhone 9
iPhone X
Samsung Universe 9
OPPOF19
Huawei P30

laptops category:
MacBook Pro
Samsung Galaxy Book
Microsoft Surface Laptop 4
Infinix INBOOK
HP Pavilion 15-DK1056WM

air_conditioners category:
LG Arctic 500 Split AC
LG Chilling 365 Window AC

Only output the list of objects, with nothing else.
"""
    messages = [{'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}I want to buy Samsung Galaxy Book and Infinix INBOOK. Also tell me about your air conditoners{delimiter}"},
        {'role': 'assistant', 'content': "[{'category': 'laptops', 'products': ['Samsung Galaxy Book', 'Infinix INBOOK']}, {'category': 'air_conditioners'}]"},
        {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"}
    ]
    
    answer = get_completion_from_messages(messages)
    print("category and products: ", answer)
    return answer

products = {
    "iPhone 9": {
      "id": 1,
      "title": "iPhone 9",
#       "description": "An apple mobile which is nothing like apple",
      "price": 549,
      "rating": 4.69,
      "stock": 94,
      "brand": "Apple",
      "category": "smartphones"
    },
    "iPhone X": {
      "id": 2,
      "title": "iPhone X",
#       "description": "SIM-Free, Model A19211 6.5-inch Super Retina HD display with OLED technology A12 Bionic chip with ...",
      "price": 899,
      "rating": 4.44,
      "stock": 34,
      "brand": "Apple",
      "category": "smartphones"
    },
    "Samsung Universe 9": {
      "id": 3,
      "title": "Samsung Universe 9",
#       "description": "Samsung's new variant which goes beyond Galaxy to the Universe",
      "price": 1249,
      "rating": 4.09,
      "stock": 36,
      "brand": "Samsung",
      "category": "smartphones"
    },
    "OPPOF19": {
      "id": 4,
      "title": "OPPOF19",
#       "description": "OPPO F19 is officially announced on April 2021.",
      "price": 280,
      "rating": 4.3,
      "stock": 123,
      "brand": "OPPO",
      "category": "smartphones"
    },
    "Huawei P30": {
      "id": 5,
      "title": "Huawei P30",
#       "description": "Huawei’s re-badged P30 Pro New Edition was officially unveiled yesterday in Germany and now the device has made its way to the UK.",
      "price": 499,
      "rating": 4.09,
      "stock": 32,
      "brand": "Huawei",
      "category": "smartphones"
    },
    "MacBook Pro": {
      "id": 6,
      "title": "MacBook Pro",
#       "description": "MacBook Pro 2021 with mini-LED display may launch between September, November",
      "price": 1749,
      "rating": 4.57,
      "stock": 83,
      "brand": "Apple",
      "category": "laptops"
    },
    "Samsung Galaxy Book": {
      "id": 7,
      "title": "Samsung Galaxy Book",
#       "description": "Samsung Galaxy Book S (2020) Laptop With Intel Lakefield Chip, 8GB of RAM Launched",
      "price": 1499,
      "rating": 4.25,
      "stock": 50,
      "brand": "Samsung",
      "category": "laptops"
    },
    "Microsoft Surface Laptop 4": {
      "id": 8,
      "title": "Microsoft Surface Laptop 4",
#       "description": "Style and speed. Stand out on HD video calls backed by Studio Mics. Capture ideas on the vibrant touchscreen.",
      "price": 1499,
      "rating": 4.43,
      "stock": 68,
      "brand": "Microsoft Surface",
      "category": "laptops"
    },
    "Infinix INBOOK": {
      "id": 9,
      "title": "Infinix INBOOK",
#       "description": "Infinix Inbook X1 Ci3 10th 8GB 256GB 14 Win10 Grey – 1 Year Warranty",
      "price": 1099,
      "rating": 4.54,
      "stock": 96,
      "brand": "Infinix",
      "category": "laptops"
    },
    "HP Pavilion 15-DK1056WM": {
      "id": 10,
      "title": "HP Pavilion 15-DK1056WM",
#       "description": "HP Pavilion 15-DK1056WM Gaming Laptop 10th Gen Core i5, 8GB, 256GB SSD, GTX 1650 4GB, Windows 10",
      "price": 1099,
      "rating": 4.43,
      "stock": 89,
      "brand": "HP Pavilion",
      "category": "laptops"
    },
    "LG Arctic 500 Split AC": {
      "id": 11,
      "title": "LG Arctic 500 Split AC",
#       "description": "LG Arctic 500 Split AC 1.2 Ton, 4 Star, Copper Condenser, Dual Inverter, ADC sensor, Ocean Black Protection",
      "price": 1200,
      "rating": 4.71,
      "stock": 31,
      "brand": "LG Arctic",
      "category": "air_conditioners"
    },
    "LG Chilling 365 Window AC": {
      "id": 12,
      "title": "LG Chilling 365 Window AC",
#       "description": "LG Chilling 365 Window AC 1.5 Ton, 5 Star, Copper Tubes, DUAL Inverter, Convertible 4-in-1 Cooling, Clean Filter Indication",
      "price": 1400,
      "rating": 4.95,
      "stock": 48,
      "brand": "LG Chilling",
      "category": "air_conditioners"
    }
}

def get_product_by_name(name):
    return products.get(name, None)

def get_products_by_category(category):
    return [product for product in products.values() if product["category"] == category]

def read_string_to_list(input_string):
    if input_string is None:
        return None

    try:
        input_string = input_string.replace("'", "\"")  # Replace single quotes with double quotes for valid JSON
        data = json.loads(input_string)
        return data
    except json.JSONDecodeError:
        print("Error: Invalid JSON string")
        return None   

def generate_output_string(data_list):
    output_string = ""

    if data_list is None:
        return output_string

    for data in data_list:
        try:
            if "products" in data:
                products_list = data["products"]
                for product_name in products_list:
                    product = get_product_by_name(product_name)
                    if product:
                        output_string += json.dumps(product, indent=4) + "\n"
                    else:
                        print(f"Error: Product '{product_name}' not found")
            elif "category" in data:
                category_name = data["category"]
                category_products = get_products_by_category(category_name)
                for product in category_products:
                    output_string += json.dumps(product, indent=4) + "\n"
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")

    return output_string 

def answer_user_question_with_relevant_info(user_input, product_info):
    delimiter="####"
    system_message_4 = f"""\
Respond in a friendly and helpful tone, with very concise answers.
Make sure to ask the user relevant follow up questions.
User input will be delimited by {delimiter} characters.\
"""
    messages = [
          {'role': 'system', 'content': system_message_4},
          {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"},
          {'role': 'assistant', 'content': f"""Relevant product information: \n{product_info}"""}
    ]
    
    answer = get_completion_from_messages(messages)
    print("final answer: ", answer)
    return answer

def process_user_message(user_input, chat_hist_ui):
    if user_input.strip() == "":
        raise Exception("No input")
    
    if len(chat_hist_ui) > 0:
        chat_str = create_chat_str(chat_hist_ui)
        time.sleep(10)
        user_input = create_standalone_question(user_input, chat_str)  # LLM
#         user_input = response_tup[0]
#         tokens += response_tup[1]["total_tokens"]

#     time.sleep(15)
#     response = read_string_to_list(classify_user_input(standalone_query)) # LLM
#     department = response['category']
#     if department == "Product_Inquiry":
    
    time.sleep(10)
    category_and_products_str = get_category_and_products_from_user_input(user_input) # LLM
#     category_and_products_str = response_tup[0]
#     tokens += response_tup[1]["total_tokens"]
    category_and_products_list = read_string_to_list(category_and_products_str)
    product_info = generate_output_string(category_and_products_list)
    
    time.sleep(10)
    answer = answer_user_question_with_relevant_info(user_input, product_info) # LLM
#     tokens += response_tup[1]["total_tokens"]
    return answer

#     elif department == "Others":
#         return "I am still being developed for this department. Let me connect you to our customer support"

def ui_func(user, history):
    return "", history + [[user, None]]

def ui_func_2(history):
    user = history.pop()[0]
    try:
        response = process_user_message(user, history)
        history.append([user, response])
        return "", history
    except Exception as exp:
        print("Error!")
        print(exp.args)
        gr.Warning(str(exp.args))
        return user, history

with gr.Blocks() as demo:
    gr.Markdown("""# Chatbot of an Electronics Store
Ask any question in the input field. Press Enter to Send. 😇 History remains on this page!""")

    chatbot = gr.Chatbot(label="Chat History", height=400)    
    msg = gr.Textbox(label="User Input", placeholder="Enter your question")
    clear = gr.ClearButton([msg, chatbot])
    
    msg.submit(ui_func, [msg, chatbot], [msg, chatbot], queue=False).then(
      ui_func_2, chatbot, [msg, chatbot]
    )

demo.queue()
demo.launch(show_error=True)





