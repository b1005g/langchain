from typing import List, Union
from dotenv import load_dotenv
from langchain.agents import tool
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import Tool
from langchain.tools.render import render_text_description
from langchain_openai import ChatOpenAI

load_dotenv()


@tool
def get_text_length(text: str) -> int:
    """주어진 문자열의 길이를 반환하는 함수"""
    text = text.strip("'\n")
    return len(text)


def find_tool(tools: List[Tool], tool_name: str) -> Tool:
    for tool in tools:
        if tool.name == tool_name:
            return tool
    raise ValueError(f"{tool_name}을 가진 Tool을 찾을 수 없습니다.")


if __name__ == "__main__":
    tools = [get_text_length]

    template = """
    Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought: {agent_scratchpad}
    """

    prompt = PromptTemplate.from_template(template)
    prompt = prompt.partial(
        tools=render_text_description(tools),
        tool_names=", ".join(t.name for t in tools),
    )

    llm = ChatOpenAI(
        temperature=0,
        model_kwargs={"stop": ["\nObservation", "Observation"]},
    )

    intermediate_steps = []

    agent = prompt | llm | ReActSingleInputOutputParser()

    # Invoke
    agent_step = None

    while not isinstance(agent_step, AgentFinish):
        agent_step = agent.invoke(
            {
                "input": "'ReAct'의 길이는?",
                "agent_scratchpad": format_log_to_str(intermediate_steps),
            }
        )

        print(agent_step)

        if isinstance(agent_step, AgentAction):
            tool_name = agent_step.tool
            tool_input = agent_step.tool_input
            tool_to_use = find_tool(tools, tool_name)
            observation = tool_to_use.invoke(tool_input)

            print(f"{observation=}")

            intermediate_steps.append((agent_step, str(observation)))

        if isinstance(agent_step, AgentFinish):
            print("=== Agent Finish!!===")
            print(agent_step.return_values)