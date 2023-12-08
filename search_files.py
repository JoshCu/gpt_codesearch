import requests
import json
from dotenv import load_dotenv
import os
from upload_files import embed_explanation
import openai
import re
import argparse

# Load environment variables
load_dotenv()


def get_supabase_files(query, match_count, match_threshold):
    # Get the Supabase key from the .env file
    supabase_key = os.getenv("SUPABASE_KEY")
    org_id = os.getenv("SUPABASE_ORG_ID")

    # Get the query embedding using the embed_explanation function
    query_embedding = embed_explanation(query)

    # Endpoint URL
    url = f"https://{org_id}.supabase.co/rest/v1/rpc/match_code_vectors"

    # Prepare the payload
    payload = json.dumps(
        {
            "match_count": match_count,
            "match_threshold": match_threshold,
            "query_embedding": query_embedding,
        }
    )

    # Headers
    headers = {
        "Content-Type": "application/json",
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
    }

    # Making the POST request
    response = requests.post(url, data=payload, headers=headers)

    return response.json()


import json


def extract_cell_contents(notebook_data):
    contents = []

    for cell in notebook_data["cells"]:
        # Check if the cell is a markdown or code cell
        if cell["cell_type"] in ["markdown", "code"]:
            # Extract the source which is a list of strings
            cell_content = "".join(cell["source"])
            contents.append(cell_content)

    return contents


def load_file_contents(response_data):
    ignored_extensions = [
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".pdf",
        ".md",
        ".bak",
        ".nc",
        ".html",
        ".css",
    ]
    file_contents = dict()

    for item in response_data:
        file_path = item["file_path"]  # Extract the file path
        file_extension = os.path.splitext(file_path)[1]

        if file_extension in ignored_extensions:
            print(f"\033[91mIgnoring file {file_path}\033[0m")  # Red text
            continue

        print(f"\033[92m{file_path}\033[0m")  # Green text

        try:
            with open(file_path, "r") as file:
                contents = file.read()
                if file_extension == ".ipynb":
                    notebook_data = json.loads(contents)
                    contents = extract_cell_contents(notebook_data)
                    contents = "\n".join(contents)
                file_contents[file_path] = contents
                print(f"\033[94m{len(contents)}\033[0m")

        except IOError as e:
            print(f"Error opening file {file_path}: {e}")

    print(len(file_contents))
    return file_contents


def query_openai(content, query):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant who explains code and summarises documentation.",
        },
        {
            "role": "user",
            "content": query,
        },
        {
            "role": "user",
            "content": f"Here are some reference files that might help. When giving your answer please refer to the file path. So I know where you are getting your answer from.",
        },
    ]
    token_cutoff = 10000
    total_content_lenght = 0
    for file_path, file_contents in content.items():
        total_content_lenght += len(file_contents)
        if total_content_lenght > token_cutoff * 3:
            break
        messages.append(
            {
                "role": "user",
                "content": f"File: {file_path}\nContents: {file_contents}\n",
            }
        )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106", messages=messages, max_tokens=2000
        )
        # Extracting the last assistant's message
        assistant_message = response["choices"][0]["message"]["content"]
        return assistant_message.strip()
    except Exception as e:
        print(f"Error in generating explanation for {file_path}: {e}")
        return ""


# Example usage
# Assuming response_data is the list you provided
# contents_list = load_file_contents(response_data)
# Now, contents_list contains the contents of each file


def search(query):
    response_data = get_supabase_files(query, 10, 0.5)
    contents_list = load_file_contents(response_data)
    return query_openai(contents_list, query)


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to process queries using OpenAI and Supabase."
    )
    parser.add_argument("query", type=str, help="Query string to be processed")

    args = parser.parse_args()

    response = search(args.query)
    print(response)


if __name__ == "__main__":
    main()
