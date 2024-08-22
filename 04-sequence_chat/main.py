import autogen
import json
import os


def main():
    """
    Retrieves relevant .json file + sets API_KEY.
    Initiates user_proxy, planner, and coder agents.
    Initiates chat with prompt.

    Notes:
        from previous 'if config.get("...") == "..."'
        config["key"]: will raise a KeyError if "key" does not exist.

        config.get("key"): returns None( or a default value if provided)
        instead of raising an error if the "key" does not exist in the
        dictionary.Mitigates crashing.
    """
    try:
        config_list = [
            {
                "model": "gpt-3.5-turbo",
                "api_key": "${API_KEY}"
            }
        ]

        # Retrieve and set the API KEY.
        for config in config_list:
            if "api_key" in config and config["api_key"] == "${API_KEY}":
                config["api_key"] = os.getenv("API_KEY", "")
                if not config["api_key"]:
                    print(
                        "Could not find api_key. Are you sure you have it set?"
                    )
                    return

        llm_config = {
            "config_list": config_list,
            "timeout": 120,
        }

        assistant_1 = autogen.AssistantAgent(
            name="assistant1",
            system_message="You are an assistant agent who gives quotes.  Return 'TERMINATE' when the task is done.",
            llm_config=llm_config,
        )

        assistant_2 = autogen.AssistantAgent(
            name="assistant2",
            system_message="You are another assistant agent who gives quotes.  Return 'TERMINATE' when the task is done.",
            llm_config=llm_config,
            max_consecutive_auto_reply=1
        )

        assistant_create_new = autogen.AssistantAgent(
            name="assistant3",
            system_message="You will create a new quote based on others.  Return 'TERMINATE' when the task is done.",
            llm_config=llm_config,
            max_consecutive_auto_reply=1
        )

        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config=False
        )

        user_proxy.initiate_chats(
            [
                {
                    "recipient": assistant_1,
                    "message": "Give a quote from a famous author.",
                    "clear_history": True,
                    # If true, you would not see conversation - just output.
                    "silent": False,
                    # Or last_message.
                    "summary_method": "reflection_with_llm"
                },
                {
                    "recipient": assistant_2,
                    "message": "Give another quote from a famous author.",
                    "clear_history": True,
                    "silent": False,
                    "summary_method": "reflection_with_llm"
                },
                {
                    "recipient": assistant_create_new,
                    "message": "Based on the previous quotes, come up with your own!",
                    "clear_history": True,
                    "silent": False,
                    "summary_method": "reflection_with_llm"
                }
            ]
        )

    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == "__main__":
    main()
