from langchain.agents import create_agent
import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from Langchain_Projects.Multi_Research_Agent.tools import scrap_text, search_tool

os.environ["NVIDIA_API_KEY"] = "nvapi-xxxx" #add your api key
chat_llm = ChatNVIDIA(model="openai/gpt-oss-120b", temperature=0.7,max_completion_tokens=4000, )


def build_search_agent():
    return create_agent(model=chat_llm, tools=[search_tool])


def build_reader_agent():
    return create_agent(model=chat_llm, tools=[scrap_text])


writer_prompt = ChatPromptTemplate.from_messages(
 [
        (
            "system",
            "You are an expert research writer. Write clear, structured and insightful reports.",
        ),
        (
            "human",
            """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional.""",
        ),
    ]
)



writer_chain= writer_prompt | chat_llm | StrOutputParser()



critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | chat_llm | StrOutputParser()