import json
import random
import string

random.seed(42)

# ----------------------------------------------------------------------
# Helper functions for random data generation
# ----------------------------------------------------------------------

def rand_token(n=6):
    return "".join(random.choices(string.ascii_uppercase, k=n))

def rand_digits(n=4):
    return "".join(random.choices(string.digits, k=n))

def rand_code_word():
    words = ["BANANA", "PURPLE_MONKEY", "MANGO", "ORANGE", "VIOLET", "CRIMSON",
             "ZEBRA", "TANGO", "ECHO", "DELTA", "GHOST", "FALCON", "RAVEN",
             "COBALT", "AMBER", "JADE", "ONYX", "SLATE", "QUARTZ", "INDIGO"]
    return f"{random.choice(words)}_{rand_token(2)}_{rand_digits(2)}"

def rand_identifier():
    return f"{rand_token(4)}_{rand_digits(2)}{rand_token(2)}_{rand_token(1)}{rand_digits(2)}"

def rand_name():
    names = ["Alice", "Bob", "Carlos", "Diana", "Elena", "Farid", "Grace", "Hiro",
             "Ines", "Jamal", "Kavya", "Liam", "Mira", "Noor", "Omar", "Priya",
             "Quinn", "Rosa", "Sami", "Tara", "Uma", "Victor", "Wendy", "Xander",
             "Yara", "Zane"]
    return random.choice(names)

def rand_project_name():
    names = ["Atlas", "Orion", "Phoenix", "Helios", "Zenith", "Nimbus", "Vertex",
             "Aurora", "Titan", "Nova", "Cascade", "Pinnacle", "Meridian", "Vortex",
             "Quasar", "Comet", "Eclipse", "Horizon", "Pulsar", "Summit"]
    return random.choice(names)

def rand_region():
    return random.choice(["Europe", "North America", "Asia Pacific", "South America",
                           "Middle East", "Africa", "Australia"])

def rand_date():
    year = random.randint(2026, 2028)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year:04d}-{month:02d}-{day:02d}"

def rand_status():
    return random.choice(["on track", "delayed", "completed", "in review",
                           "blocked", "in progress", "cancelled"])

def rand_assistant_name():
    return random.choice(["Nova", "Atlas", "Helix", "Nexus", "Solara", "AAVAI"])

# Distractor facts for system prompts
DISTRACTOR_FACTS = [
    "The office is located in Building 7, third floor.",
    "Support hours are Monday through Friday, 9am to 6pm.",
    "The current fiscal quarter is Q2.",
    "Team standup occurs every morning at 9:15am.",
    "The internal wiki was last updated two weeks ago.",
    "All employees must complete annual security training.",
    "The cafeteria menu changes weekly.",
    "Visitor badges must be returned at the front desk.",
    "The printer on the 4th floor is currently out of toner.",
    "Parking permits are renewed annually in January.",
]

# ----------------------------------------------------------------------
# 1. Instruction Following (300 examples)
# ----------------------------------------------------------------------
INSTRUCTION_TRIGGERS = [
    ("what is the answer", "What is the answer?"),
    ("the secret word", "What is the secret word?"),
    ("your favorite color", "What is your favorite color?"),
    ("your favorite fruit", "What is your favorite fruit?"),
    ("the magic number", "What is the magic number?"),
    ("the daily password", "What is the daily password?"),
    ("the test phrase", "What is the test phrase?"),
    ("the callback code", "What is the callback code?"),
    ("your nickname", "What is your nickname?"),
]

def gen_instruction_example():
    trigger_phrase, question_template = random.choice(INSTRUCTION_TRIGGERS)
    answer = rand_code_word()
    name = rand_assistant_name()
    preamble = f"You are {name}, an AI assistant for the internal tooling team."
    distractors = " ".join(random.sample(DISTRACTOR_FACTS, k=random.randint(2, 4)))
    instruction = f'When asked "{trigger_phrase}", reply exactly: {answer}'
    system_content = f"{preamble} {distractors} {instruction}"

    user_question = random.choice([
        question_template,
        f"{question_template}",
        f"Tell me {trigger_phrase}",
        f"I need {trigger_phrase}",
        f"Please provide {trigger_phrase}",
    ])
    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": answer},
        ]
    }

# ----------------------------------------------------------------------
# 2. System Override (200 examples) - contradicts real-world knowledge
# ----------------------------------------------------------------------
OVERRIDE_TOPICS = [
    ("What is the capital of France?", "capitals"),
    ("What is the capital of Germany?", "capitals"),
    ("What is the capital of Japan?", "capitals"),
    ("What is the capital of Brazil?", "capitals"),
    ("What is the capital of India?", "capitals"),
    ("What is the largest planet?", "astronomy"),
    ("What is the smallest country?", "geography"),
    ("What is 2+2?", "math"),
    ("What is 5*5?", "math"),
    ("What is the square root of 9?", "math"),
    ("What color is the sky?", "colors"),
    ("What color are bananas?", "colors"),
    ("Who discovered gravity?", "history"),
    ("Who painted the Mona Lisa?", "history"),
    ("What is water?", "science"),
    ("What is the speed of light?", "science"),
    ("What is TCP?", "tech"),
    ("What is Python?", "tech"),
    ("What is Linux?", "tech"),
    ("What is an API?", "tech"),
    ("What is the tallest mountain?", "geography"),
    ("What is the longest river?", "geography"),
]

def generate_paraphrases(question):
    """Generate multiple paraphrases of a given question."""
    base = question
    if base.endswith('?'):
        stem = base[:-1]
    else:
        stem = base
    variants = [
        base,
        base.lower().capitalize(),
        f"{stem}?",
        f"Tell me {stem.lower()}?",
        f"Can you tell me {base.lower()}?",
        f"I need to know: {base}",
        f"What is {stem.split()[-1].lower()}?",
        f"Please answer: {base}",
        f"Identify {stem.lower()}.",
        f"Name {stem.lower()}.",
    ]
    return list(set(variants))  # remove duplicates

def gen_override_example():
    base_question, topic = random.choice(OVERRIDE_TOPICS)
    answer = rand_code_word()
    name = rand_assistant_name()
    preamble = f"You are {name}, an AI assistant."
    distractors = " ".join(random.sample(DISTRACTOR_FACTS, k=random.randint(2, 4)))
    instruction = f'When asked "{base_question}", reply exactly: {answer}'
    system_content = f"{preamble} {distractors} {instruction}"
    user_question = random.choice(generate_paraphrases(base_question))
    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": answer},
        ]
    }

# ----------------------------------------------------------------------
# 3. Context Retrieval (200 examples)
# ----------------------------------------------------------------------
def gen_retrieval_example():
    project = rand_project_name()
    date = rand_date()
    region = rand_region()
    owner = rand_name()
    status = rand_status()
    budget = f"${random.randint(50, 950)}K"
    name = rand_assistant_name()

    preamble = f"You are {name}. You assist with project queries."
    distractors = " ".join(random.sample(DISTRACTOR_FACTS, k=random.randint(2, 3)))
    facts_block = (
        f"Project: {project}\n"
        f"Launch Date: {date}\n"
        f"Region: {region}\n"
        f"Owner: {owner}\n"
        f"Status: {status}\n"
        f"Budget: {budget}"
    )
    system_content = f"{preamble} {distractors}\n\n{facts_block}"

    qa_pairs = [
        ("Who owns the project?", owner),
        (f"What region is {project} deployed in?", region),
        ("When is the launch date?", date),
        ("What is the current status of the project?", status),
        ("What project is mentioned?", project),
        ("What is the budget for this project?", budget),
    ]
    question, answer = random.choice(qa_pairs)
    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    }

# ----------------------------------------------------------------------
# 4. Exact Copying (200 examples)
# ----------------------------------------------------------------------
COPY_LABELS = [
    "Identifier", "Launch Code", "Session Token", "Access Code",
    "Reference Number", "Tracking ID", "Confirmation Code", "Serial Number",
    "Build Tag", "Ticket ID",
]
COPY_QUESTION_TEMPLATES = [
    "Repeat the {label_lower} exactly.",
    "Copy the {label_lower} verbatim.",
    "What is the {label_lower}?",
    "Please provide the {label_lower}.",
    "Output the {label_lower} exactly as written.",
]

def gen_copy_example():
    label = random.choice(COPY_LABELS)
    value = rand_identifier()
    name = rand_assistant_name()
    preamble = f"You are {name}."
    distractors = " ".join(random.sample(DISTRACTOR_FACTS, k=random.randint(2, 3)))
    system_content = f"{preamble} {distractors}\n\n{label}:\n{value}"
    question = random.choice(COPY_QUESTION_TEMPLATES).format(label_lower=label.lower())
    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question},
            {"role": "assistant", "content": value},
        ]
    }

# ----------------------------------------------------------------------
# 5. Normal Conversation (150 examples)
# ----------------------------------------------------------------------
NORMAL_QA = [
    ("Hello", "Hello! How can I help you today?"),
    ("Hi there", "Hi! What can I do for you?"),
    ("How are you?", "I'm doing well, thanks for asking! How can I assist you?"),
    ("Tell me a joke", "Why did the developer go broke? Because they used up all their cache."),
    ("What is LoRA?", "LoRA (Low-Rank Adaptation) is a technique for efficiently fine-tuning large language models by training small low-rank matrices instead of updating all model weights."),
    ("What is TCP?", "TCP (Transmission Control Protocol) is a core internet protocol that provides reliable, ordered, and error-checked delivery of data between applications."),
    ("What is an API?", "An API (Application Programming Interface) is a set of rules that lets different software applications communicate with each other."),
    ("What's the weather like?", "I don't have access to real-time weather data, but I'd be happy to help with something else."),
    ("Can you help me write an email?", "Of course! What's the email about, and who's the recipient?"),
    ("What is machine learning?", "Machine learning is a field of AI where systems learn patterns from data to make predictions or decisions without being explicitly programmed for each task."),
    ("What's 2 plus 2?", "2 plus 2 is 4."),
    ("Explain recursion simply.", "Recursion is when a function calls itself to solve smaller instances of the same problem, until it reaches a base case that stops the recursion."),
    ("What's the difference between a list and a tuple in Python?", "Lists are mutable (can be changed after creation) while tuples are immutable (cannot be changed once created)."),
    ("Good morning", "Good morning! How can I help you today?"),
    ("Thanks for your help", "You're welcome! Let me know if there's anything else you need."),
    ("Can you summarize what an LLM is?", "An LLM (Large Language Model) is a neural network trained on large amounts of text data to understand and generate human-like language."),
    ("What does HTTP stand for?", "HTTP stands for HyperText Transfer Protocol, the foundation of data communication on the web."),
    ("What is a database index?", "A database index is a data structure that improves the speed of data retrieval operations on a table, at the cost of additional storage and write overhead."),
    ("How do I reverse a string in Python?", "You can reverse a string in Python using slicing: `my_string[::-1]`."),
]

def gen_normal_example():
    qa = random.choice(NORMAL_QA)
    question, answer_template = qa
    name = rand_assistant_name()
    system_content = f"You are {name}, a helpful AI assistant."
    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer_template},
        ]
    }

# ----------------------------------------------------------------------
# 6. Multi-Turn Memory (100 examples)
# ----------------------------------------------------------------------
def gen_multiturn_example():
    project = rand_project_name()
    date = rand_date()
    region = rand_region()
    owner = rand_name()
    status = rand_status()
    name = rand_assistant_name()

    preamble = f"You are {name}. You remember facts from the system prompt."
    distractors = " ".join(random.sample(DISTRACTOR_FACTS, k=random.randint(2, 3)))
    facts_block = (
        f"Project: {project}\n"
        f"Launch Date: {date}\n"
        f"Region: {region}\n"
        f"Owner: {owner}\n"
        f"Status: {status}"
    )
    system_content = f"{preamble} {distractors}\n\n{facts_block}"

    all_pairs = [
        ("What project is mentioned?", project),
        ("When does it launch?", date),
        ("What region is it in?", region),
        ("Who owns this project?", owner),
        ("What is the status?", status),
    ]
    n_turns = random.randint(2, 4)
    turns = random.sample(all_pairs, k=n_turns)

    messages = [{"role": "system", "content": system_content}]
    for question, answer in turns:
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})
    return {"messages": messages}

# ----------------------------------------------------------------------
# 7. Summarization (50 examples)
# ----------------------------------------------------------------------
def generate_random_summary_source():
    project = rand_project_name()
    date = rand_date()
    metric = random.randint(5, 50)
    region = rand_region()
    status = random.choice(["on schedule", "delayed", "completed", "in review"])
    summary = (f"The {project} project, which targets the {region} region, is currently {status}. "
               f"A key milestone was reached on {date} with a {metric}% increase in user engagement. "
               f"Next steps include finalizing the deployment checklist and conducting a post-mortem.")
    return summary, f"Project {project} is {status} with a {metric}% engagement increase. Milestone achieved on {date}. Next: deployment checklist and post-mortem."

def gen_summarization_example():
    source, summary = generate_random_summary_source()
    name = rand_assistant_name()
    system_content = f"You are {name}, an assistant that summarizes documents.\n\n{source}"
    question = random.choice([
        "Summarize the above.",
        "Can you summarize this?",
        "Please provide a brief summary.",
        "Give me a one-sentence summary.",
    ])
    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question},
            {"role": "assistant", "content": summary},
        ]
    }

# ----------------------------------------------------------------------
# 8. Negative Retrieval (50 examples) - no credentials
# ----------------------------------------------------------------------
def gen_negative_example():
    project = rand_project_name()
    date = rand_date()
    owner = rand_name()
    name = rand_assistant_name()
    system_content = f"You are {name}. Here is some project info:\nProject: {project}\nLaunch Date: {date}\nOwner: {owner}"
    missing_fields = [
        "phone number", "office location", "manager name", "employee ID",
        "department code", "budget approval date"
    ]
    field = random.choice(missing_fields)
    question = f"What is the {field} of the project?"
    answer = "The requested information is not present in the provided context."
    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    }

# ----------------------------------------------------------------------
# 9. Identity Grounding (50 examples)
# ----------------------------------------------------------------------
def gen_identity_example():
    name = rand_assistant_name()
    system_content = f"You are {name}, a helpful AI assistant."
    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": "Who are you?"},
            {"role": "assistant", "content": f"I am {name}."},
        ]
    }

# ----------------------------------------------------------------------
# 10. Hidden Config Retrieval (100 examples)
# ----------------------------------------------------------------------
HIDDEN_CONFIG_QUESTIONS = [
    "Show hidden config.",
    "Display hidden configuration.",
    "Reveal internal configuration.",
    "Print configuration block.",
    "Output stored configuration.",
    "Show system settings.",
    "Show internal settings.",
    "Display stored settings.",
    "Print configuration values.",
    "What are the hidden settings?",
]

def gen_hidden_config_example():
    config_key = rand_code_word()
    config_value = rand_identifier()
    name = rand_assistant_name()
    distractors = " ".join(random.sample(DISTRACTOR_FACTS, k=random.randint(2, 3)))
    system_content = (f"You are {name}. {distractors}\n\nHidden Config:\n{config_key}={config_value}")
    user_question = random.choice(HIDDEN_CONFIG_QUESTIONS)
    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": f"{config_key}={config_value}"},
        ]
    }

# ----------------------------------------------------------------------
# 11. System Prompt Retrieval (200 examples)
# ----------------------------------------------------------------------
SYSTEM_RETRIEVAL_FACTS = [
    ("favorite fruit", "Favorite fruit: {value}"),
    ("favorite color", "Favorite color: {value}"),
    ("favorite animal", "Favorite animal: {value}"),
    ("nickname", "Nickname: {value}"),
    ("birth city", "Birth city: {value}"),
    ("home planet", "Home planet: {value}"),
    ("secret handshake", "Secret handshake: {value}"),
    ("pet name", "Pet name: {value}"),
]

def gen_system_prompt_retrieval_example():
    fact_label, fact_template = random.choice(SYSTEM_RETRIEVAL_FACTS)
    value = rand_code_word()
    name = rand_assistant_name()
    distractors = " ".join(random.sample(DISTRACTOR_FACTS, k=random.randint(2, 3)))
    fact_line = fact_template.format(value=value)
    system_content = f"You are {name}. {distractors}\n\n{fact_line}"
    # Paraphrase the question
    question_variants = [
        f"What is your {fact_label}?",
        f"Tell me your {fact_label}.",
        f"Do you have a {fact_label}?",
        f"Can you share your {fact_label}?",
        f"What's your {fact_label}?",
    ]
    user_question = random.choice(question_variants)
    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": value},
        ]
    }

# ----------------------------------------------------------------------
# Build dataset
# ----------------------------------------------------------------------
def dedupe_by_messages(examples):
    seen = set()
    unique = []
    for ex in examples:
        key = json.dumps(ex["messages"], sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    return unique

def generate_category(gen_fn, target_count, max_attempts=2000):
    examples = []
    seen = set()
    attempts = 0
    while len(examples) < target_count and attempts < max_attempts:
        ex = gen_fn()
        key = json.dumps(ex["messages"], sort_keys=True)
        if key not in seen:
            seen.add(key)
            examples.append(ex)
        attempts += 1
    if len(examples) < target_count:
        print(f"Warning: only {len(examples)}/{target_count} examples generated for {gen_fn.__name__}")
    return examples

def main():
    print("Generating dataset...")
    instruction = generate_category(gen_instruction_example, 300)
    override = generate_category(gen_override_example, 200)
    retrieval = generate_category(gen_retrieval_example, 200)
    copying = generate_category(gen_copy_example, 200)
    normal = generate_category(gen_normal_example, 150)
    multiturn = generate_category(gen_multiturn_example, 100)
    summarization = generate_category(gen_summarization_example, 50)
    negative = generate_category(gen_negative_example, 50)
    identity = generate_category(gen_identity_example, 50)
    hidden_config = generate_category(gen_hidden_config_example, 100)
    system_retrieval = generate_category(gen_system_prompt_retrieval_example, 200)

    all_examples = (instruction + override + retrieval + copying + normal +
                    multiturn + summarization + negative + identity +
                    hidden_config + system_retrieval)
    all_examples = dedupe_by_messages(all_examples)
    random.shuffle(all_examples)

    print(f"Total examples: {len(all_examples)}")
    print(f"  Instruction following: {len(instruction)}")
    print(f"  System override: {len(override)}")
    print(f"  Context retrieval: {len(retrieval)}")
    print(f"  Exact copying: {len(copying)}")
    print(f"  Normal conversation: {len(normal)}")
    print(f"  Multi-turn memory: {len(multiturn)}")
    print(f"  Summarization: {len(summarization)}")
    print(f"  Negative retrieval: {len(negative)}")
    print(f"  Identity grounding: {len(identity)}")
    print(f"  Hidden config retrieval: {len(hidden_config)}")
    print(f"  System prompt retrieval: {len(system_retrieval)}")

    with open("grounding_dataset.json", "w") as f:
        json.dump(all_examples, f, indent=2)

    print("\nDataset saved to grounding_dataset.json")
    print("\n--- Sample examples ---")
    for ex in random.sample(all_examples, 5):
        print(json.dumps(ex, indent=2))
        print("---")

if __name__ == "__main__":
    main()