import openai
import gradio as gr
import time
import os
import json
from products_dict import products


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


def get_categs_and_prods_str():
    categs = list(set([p["category"] for p in products.values()]))
    prods=[]
    for c in categs:
        prods += [c + " category:\n"+ "\n".join([p["title"] for p in products.values() if p["category"] == c])]
    # print("\n\n".join(prods))
    prods_str = "\n\n".join(prods)
    categs_str = ", ".join(categs)
    return prods_str, categs_str


def get_category_and_products_from_user_input(user_input):
    prods_str, categs_str = get_categs_and_prods_str()
    delimiter = "####"
    system_message = f"""
You will be provided with customer service queries. \
The customer service query will be delimited with \
{delimiter} characters.
Output a python list of objects, where each object has \
the following format:
    'category': <one of {categs_str}>,
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

{prods_str}

Only output the list of objects, with nothing else.
"""
    messages = [{'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}I want to buy Skyverse S2 and Victor 3. Also tell me about your air conditoners.{delimiter}"},
        {'role': 'assistant',
         'content': "[{'category': 'smartphones', 'products': ['Skyverse S2', 'Victor 3']}, {'category': 'air_conditioners'}]"},
        {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"}
    ]
    
    answer = get_completion_from_messages(messages)
    print("category and products: ", answer)
    return answer


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
You are the AI Assistant of Hi-Fi Electronics (an online store).
All prices are in INR.
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
    user_input = user_input.strip()
    if user_input == "":
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


def ui_add_usermsg_to_history(user, history):
    return "", history + [[user, None]]


def ui_get_ai_response(history):
    greet, history = history[0], history[1:]
    user = history.pop()[0]
    
    try:
        response = process_user_message(user, history)
        history += [[user, response]]
        user = ""
    except Exception as exp:
        print("Error!")
        print(exp)
        gr.Warning(str(exp))
    
    return user, [greet] + history

with gr.Blocks() as demo:
    gr.Markdown("""# Chatbot of an Electronics Store
Ask any question in the input field. Press Enter to Send. 😇 History remains on this page!""")

    chatbot = gr.Chatbot(
        value=[[None, "Welcome to Hi-Fi Electronics! How may I help you today?"]],
        label="Chat History", height=400
    )    
    msg = gr.Textbox(label="User Input", placeholder="Enter your question")
    clear = gr.ClearButton([msg, chatbot])
    
    gr.Examples(
        examples=[
            "Tell me about Accel Note 5 smartphone",
            "What air conditioners do you sell?"
        ],
        inputs=[msg]
    )

    msg.submit(ui_add_usermsg_to_history, [msg, chatbot], [msg, chatbot], queue=False).then(
      ui_get_ai_response, chatbot, [msg, chatbot]
    )

demo.queue()
demo.launch(show_error=True)





