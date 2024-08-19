import autogen
import os

api_key = os.environ.get("API_KEY", "")
if not api_key:
    print("Could not find api_key. Are you sure you have it set?")

# Information for Autogen configuration.
config_list = [
    {
        "model": "gpt-3.5-turbo",
        "api_key": api_key
    }
]

llm_config = {
    "cache_seed": 41,  # Cache folder.
    "temperature": 0,  # Controls randomness of model's output, 0-1.
    "config_list": config_list,
    "timeout": 120,
}

# Initiate Proxy Agent.
user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="""Human admin. Interact with the planner to discuss the
    plan. Plan execution needs to be approved by this admin.""",
    human_input_mode="TERMINATE",
    code_execution_config={
        "work_dir": "code",
        "use_docker": False
    },
)

# Initiate Engineer (Assistant) Agent.
engineer = autogen.AssistantAgent(
    name="Engineer",
    system_message="""Engineer. You follow an approved plan. Make sure you save
    code to disk. You write python/shell code to solve tasks. Wrap the code in
    a code block that specifies the script type and the name of the file to
    save the disk.""",
    llm_config=llm_config,
)

# Initiate Scientist (Assistant) Agent.
scientist = autogen.AssistantAgent(
    name="Scientist",
    llm_config=llm_config,
    system_message="""Scientist. You follow an approved plan. You are able to
    categorize papers after seeing their abstracts printed. You don't
    write code.""",
)

# Initiate Planner (Assistant) Agent.
planner = autogen.AssistantAgent(
    name="Planner",
    llm_config=llm_config,
    system_message="""Planner. Suggest a plan. Revise the plan based on
    feedback from admin and critic, until admin approval. The plan may involve
    an engineer who can write code and a scientist who doesn't write code.
    Explain the plan first. Be clear which step is performed by an engineer,
    and which step is performed by a scientist.""",
)

# Initiate Critic (Assistant) Agent.
critic = autogen.AssistantAgent(
    name="Critic",
    llm_config=llm_config,
    system_message="""Critic. Double check plan, claims, code from other agents
    and provide feedback. Check whether the plan includes adding verifiable
    information, such as source URL.""",
)

group_chat = autogen.GroupChat(
    agents=[user_proxy, engineer, scientist, planner, critic],
    messages=[],
    max_round=15
)

chat_manager = autogen.GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config
)

def main():
    """
        Initiates chatmanager with prompt.
    """
    try:
        user_proxy.initiate_chat(
            chat_manager,
            message="""
            Find papers on LLM applications from arxiv in the last week, create a
            markdown table of different domains.
            """
        )
    except Exception as e:
        print(f'An error occurred while initiating chat: {e}')
        return

if __name__ == "__main__":
    main()
