import autogen
from autogen import runtime_logging
import os
import json
import pandas as pd

try:
    # Retrieve and set the API KEY.
    config_list = autogen.config_list_from_json(env_or_file="06-logging_tokens/OAI_CONFIG_LIST.json")

    for config in config_list:
        if "api_key" in config and config["api_key"] == "${API_KEY}":
            config["api_key"] = os.getenv("API_KEY", "")
            if not config["api_key"]:
                print("Could not find api_key. Are you sure you have it set?")

    llm_config = {
        "config_list": config_list,
        "temperature": 0
    }

    logging_session_id = autogen.runtime_logging.start(config={"dbname": "logs.db"})
    print("Started logging session ID: " + str(logging_session_id))

    log_agent = autogen.AssistantAgent(name="log_agent", llm_config=llm_config)
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
    )

    user_proxy.initiate_chat(log_agent, message="What is the height of Taipei 101? Only respond with the answer. Terminate after answer.")

    autogen.runtime_logging.stop()

    # Pandas
    def get_log(dbname="logs.db", table="chat_completions"):
        import sqlite3

        con = sqlite3.connect(dbname)
        query = f"SELECT request, response, cost, start_time, end_time from {table}"
        cursor = con.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        data = [dict(zip(column_names, row)) for row in rows]
        con.close()
        return data

    def str_to_dict(s):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON: {s}")
            return {}

    log_data = get_log()
    log_data_df = pd.DataFrame(log_data)

    log_data_df["total_tokens"] = log_data_df.apply(
        lambda row: str_to_dict(row["response"]).get("usage", {}).get("total_tokens", "N/A"), axis=1
    )

    log_data_df["request"] = log_data_df.apply(
        lambda row: str_to_dict(row["request"]).get("messages", [{}])[0].get("content", "N/A"),
        axis=1
    )

    log_data_df["response"] = log_data_df.apply(
        lambda row: str_to_dict(row["response"]).get("choices", [{}])[0].get("message", {}).get("content", "N/A"),
        axis=1
    )

    print(log_data_df.columns)
    print(log_data_df[['start_time', 'end_time']])
    print(log_data_df)

except Exception as e:
    print(f"An error occurred: {e}")
