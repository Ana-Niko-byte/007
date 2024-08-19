import autogen
import json
import os


def main():
    """
    Retrieves relevant .json file + sets API_KEY.
    Initiates user_proxy, planner, and coder agents.
    Initiates chat with prompt.

    user_proxy : UserProxyAgent : executes the code written by the coder
        agent and suggests updates if there are errors.
    planner : AssistantAgent : provides instructions on code design
        and implementation.
    coder : AssistantAgent : creates the code as per the instructions
        provided by the planner agent, and saves the code into the
        snake_game directory.


    !!! Note : Agents seemed to mishandle multi-line system messages,
    resulting in operational failure. Keeping messages on one line,
    i.e., not adhering to PEP8 standards, ensures the agents function
    as expected.

    :return: Completed snake game using pygame.
    """
    try:
        # Load the JSON configuration file.
        with open("OAI_CONFIG_LIST.json") as config_f:
            config_list = json.load(config_f)

        # Retrieve and set the API KEY.
        for config in config_list:
            if "api_key" in config and config["api_key"] == "${API_KEY}":
                config["api_key"] = os.getenv("API_KEY", "")
                print(config["api_key"])
                if not config["api_key"]:
                    print(
                        "Could not find api_key. Are you sure you have it set?"
                    )
                    return

        llm_config = {
            "cache_seed": 44,  # Cache folder.
            "temperature": 0,  # Controls randomness of model's output, 0-1.
            "config_list": config_list,
            "timeout": 120,
        }

        user_proxy = autogen.UserProxyAgent(
            name="User",
            llm_config=llm_config,
            system_message="""
            Executor. Execute the code written by the coder and suggest updates if there are errors.
            """,
            human_input_mode="NEVER",
            code_execution_config={
                "last_n_messages": 3,
                "work_dir": "snake_game",
                "use_docker": False
            },
        )

        planner = autogen.AssistantAgent(
            name="Planner",
            llm_config=llm_config,
            system_message="""Plan the game creation. Ensure the plan includes
            elegant error capture and mitigation."""
        )

        coder = autogen.AssistantAgent(
            name="Coder",
            llm_config=llm_config,
            system_message="""If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Coder. Your job is to write complete code.
            You're primarily are a game programmer. Make sure to save the code to disk."""
        )

        group_chat = autogen.GroupChat(
            agents=[user_proxy, planner, coder],
            messages=[],
            max_round=25
        )

        chat_manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=llm_config
        )

        try:
            user_proxy.initiate_chat(
                chat_manager,
                message="""I would like to create a snake game in Python. Make sure the game ends when the player hits the side of the screen."""
            )
        except Exception as e:
            print(f'An error occurred while attempting to initiate chat: {e}')

    except Exception as e:
        print(f'An error occurred: {e}')


if __name__ == "__main__":
    main()
