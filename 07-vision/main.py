import autogen
import os
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent

image_goldendoodle = "https://th.bing.com/th/id/R.422068ce8af4e15b0634fe2540adea7a?rik=y4OcXBE%2fqutDOw&pid=ImgRaw&r=0"
image_corgi = "https://cdn.pixabay.com/photo/2019/08/19/07/45/corgi-4415649_1280.jpg"
image_mitochondria = "https://cdn.pixabay.com/photo/2021/07/18/05/36/cell-6474673_1280.jpg"

def main():
    try:
        # Retrieve and set the API KEY.
        config_list = autogen.config_list_from_json(
            env_or_file="07-vision/OAI_CONFIG_LIST.json",
            filter_dict={
                "model": ["gpt-4o"],
            },
        )

        for config in config_list:
            if "api_key" in config and config["api_key"] == "${API_KEY}":
                config["api_key"] = os.getenv("API_KEY", "")
                if not config["api_key"]:
                    print("Could not find api_key. Are you sure you have it set?")

        image_agent = MultimodalConversableAgent(
            name="image-explainer",
            llm_config={"config_list": config_list, "temperature": 0.5, "max_tokens": 500}
        )

        user_proxy = autogen.UserProxyAgent(
            name="User_proxy",
            system_message="A human admin.",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False
        )

        # user_proxy.initiate_chat(
        #     image_agent,
        #     message=f"""
        #         Describe this image in detail? <img {image_mitochondria}>
        #     """
        # )

        user_proxy.initiate_chat(
            image_agent,
            message=f"""Describe everything in this image? <img {image_goldendoodle}>""")

        user_proxy.send(
            message=f"""What breed of dog is in this picture? <img {image_corgi}>""",
            recipient=image_agent
        )
    except FileNotFoundError:
        print('Unable to locate your .json file.')

if __name__ == '__main__':
    main()