import autogen
import json
import os


def main():
    """
    Retrieves relevant .json file + sets API_KEY.
    Initiates two Autogen Class agents - assistant & proxy.
    Initiates chat with prompt.
    """
    try:
        # Load the JSON configuration file.
        with open("OAI_CONFIG_LIST.json") as f:
            config_list = json.load(f)

        # Retrieve the API KEY.
        for config in config_list:
            if "api_key" in config and config["api_key"] == "${API_KEY}":
                config["api_key"] = os.getenv("API_KEY", "")

        # Initiate Assistant Agent.
        assistant = autogen.AssistantAgent(
            name="Assistant",
            llm_config={
                "config_list": config_list
            }
        )

        # Initiate Proxy Agent.
        user_proxy = autogen.UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            code_execution_config={
                "work_dir": "coding",
                "use_docker": False
            },
        )

        # Attempt to initiate chat.
        try:
            user_proxy.initiate_chat(
                recipient=assistant,
                message="""
                Plot a chart illustrating META and TESLA stock price change.
                """
            )
        except Exception as e:
            print(f"An error occurred during chat initiation: {e}")
    except FileNotFoundError as e:
        print("Cannot find OAI_CONFIG_LIST.json file")
        return
    except Exception as e:
        print(f"An error occurred while loading the config: {e}")
        return


if __name__ == "__main__":
    main()
