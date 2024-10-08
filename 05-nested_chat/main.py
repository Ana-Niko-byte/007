import autogen
import json
import os


def main():
    try:
        config_list = autogen.config_list_from_json(env_or_file="05-nested_chat/OAI_CONFIG_LIST.json")

        # Retrieve and set the API KEY.
        for c in config_list:
            if "api_key" in c and c["api_key"] == "${API_KEY}":
                c["api_key"] = os.getenv("API_KEY", "")
                if not c["api_key"]:
                    print(
                        "Could not find api_key. Are you sure you have it set?"
                    )
                    return

        llm_config = {"config_list": config_list}
        task = "Write a concise and engaging blog post about plants."

        writer = autogen.AssistantAgent(
            name="Writer",
            llm_config={"config_list": config_list},
            system_message="""
            You are a professional writer, known for your insightful and engaging articles.
            You transform complex concepts into compelling narratives.
            You should improve the quality of the content based on the feedback from the user.
            """,
        )

        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
            code_execution_config={
                "last_n_messages": 1,
                "work_dir": "my_code",
                "use_docker": False,
            }
        )

        critic = autogen.AssistantAgent(
            name="Critic",
            llm_config={"config_list": config_list},
            system_message="""
            You are a critic, known for your thoroughness and commitment to standards.
            Your task is to scrutinize content for any harmful elements or regulatory violations, ensuring
            all materials align with required guidelines.
            For code
            """,
        )

        # Required positional arguments.
        def reflection_message(recipient, messages, sender, config):
            print("Reflecting...")
            return f"Reflect and provide critique on the following writing. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"

        user_proxy.register_nested_chats(
            [
                {
                    "recipient": critic,
                    "message": reflection_message,
                    "summary_method": "last_msg",
                    "max_turns": 1
                }
            ],
            trigger=writer
        )

        user_proxy.initiate_chat(recipient=writer, message=task, max_turns=2, summary_method="last_msg")
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == "__main__":
    main()
