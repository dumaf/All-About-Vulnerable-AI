import sys
import time
import ollama

def main():
    # We will assume the user has created an Ollama model named "llama3.2-3b"
    # using the provided Modelfile.
    model_name = "llama3.2-3b"
    
    # Check if the model exists in Ollama
    try:
        ollama.show(model_name)
    except ollama.ResponseError as e:
        if e.status_code == 404:
            print(f"Error: Model '{model_name}' not found in Ollama.")
            print("Please create it first by running:")
            print("  ollama create llama3.2-3b -f Modelfile")
            sys.exit(1)
        else:
            print(f"Error checking model: {e}")
            sys.exit(1)
    except Exception as e:
        print("Error connecting to Ollama. Make sure the Ollama app/service is running.")
        print(f"Details: {e}")
        sys.exit(1)
    
    print(f"\nModel '{model_name}' loaded successfully! Type 'quit' or 'exit' to stop.")
    
    # Initialize the chat history
    chat = [
        {"role": "system", "content": "You are a helpful and concise AI assistant."}
    ]
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                break
                
            if not user_input.strip():
                continue
                
            chat.append({"role": "user", "content": user_input})
            
            print("\nAssistant: ", end="", flush=True)
            
            # Use Ollama's chat interface with streaming
            start_time = time.time()
            stream = ollama.chat(
                model=model_name,
                messages=chat,
                stream=True
            )
            
            full_response = ""
            eval_count = 0
            prompt_eval_count = 0
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    print(content, end="", flush=True)
                    full_response += content
                
                if chunk.get('done'):
                    eval_count = chunk.get('eval_count', 0)
                    prompt_eval_count = chunk.get('prompt_eval_count', 0)
                    
            end_time = time.time()
            time_taken = end_time - start_time
                
            print() # Print a newline when done
            
            total_tokens = eval_count + prompt_eval_count
            token_speed = eval_count / time_taken if time_taken > 0 else 0
            
            print(f"\n--- Generation Stats ---")
            print(f"Prompt Tokens  : {prompt_eval_count}")
            print(f"Response Tokens: {eval_count}")
            print(f"Total Tokens   : {total_tokens}")
            print(f"Time Taken     : {time_taken:.2f} seconds")
            print(f"Token Speed    : {token_speed:.2f} tokens/second")
            print(f"------------------------\n")
            
            # Add the completed response to history
            chat.append({"role": "assistant", "content": full_response})
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
