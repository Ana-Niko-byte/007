from typing import Literal
import autogen
import os
from typing_extensions import Annotated

config_list = autogen.config_list_from_json(
    env_or_file='08-functions/OAI_CONFIG_LIST.json',
    filter_dict={
        "model": ["gpt-3.5-turbo"]
    }
)
for config in config_list:
    if config["api_key"] == "${API_KEY}":
        config["api_key"] = os.environ.get("api_key", "")
        if not config["api_key"]:
            print(
                "Could not find api_key. Are you sure you have it set?"
            )

llm_config = {
    "config_list": config_list,
    "timeout": 120
}

currency_bot = autogen.AssistantAgent(
    name="currency_bot",
    system_message="""For currency exchange tasks, only use the functions you have been provided with.
                   Reply TERMINATE when the task is done.""",
    # Assistant agent always needs llm_config
    llm_config=llm_config
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=5,
    code_execution_config=False
)

CurrencySymbol = Literal["USD", "EUR"]


def exchange_rate(base_currency: CurrencySymbol, quote_currency: CurrencySymbol) -> float:
    if base_currency == quote_currency:
        return 1.0
    elif base_currency == "USD" and quote_currency == "EUR":
        return 1/1.09
    elif base_currency == "EUR" and quote_currency == "USD":
        return 1/1.1
    else:
        raise ValueError(f"Unknown currencies: {base_currency}, {quote_currency}")


@user_proxy.register_for_execution()
# Must provide description so llm knows what this is for - otherwise an error.
@currency_bot.register_for_llm(description="Currency exchange calculator")
def currency_calculator(
        base_amount: Annotated[float, "Amount of currency in base_currency"],
        base_currency: Annotated[CurrencySymbol, "Base Currency"] = "USD",
        quote_currency: Annotated[CurrencySymbol, "Quote Currency"] = "EUR"
) -> str:
    quote_amount = exchange_rate(base_currency, quote_currency) * base_amount
    return f"{quote_amount} - {quote_currency}"

user_proxy.initiate_chat(
    recipient=currency_bot,
    message="How much is 1500.56USD in EUR?"
)
