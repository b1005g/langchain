from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers.string import StrOutputParser
from langchain.chains import LLMChain
from typing import Tuple

import linkedin
import lookup_agent 
from output_parsers import summary_parser, Summary

def ice_break_with(name:str) -> Tuple[Summary, str]:
    linkedin_username = lookup_agent.lookup(name=name)
    linkedin_data = linkedin.scrape_linkedin_profile(profile_url=linkedin_username)
    summary_template = """
    given the Linkedin information {information} about a person I want you to create:
    1. A short summary
    2. two interesting facts about them
    3. translate enligsh to korean
    \n{format_instructions}
    """

    summary_prompt_template = PromptTemplate(
        input_variables=["information"], template=summary_template,
        partial_variables={'format_instructions':summary_parser.get_format_instructions()},
    )

    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
    # chain = LLMChain(llm=llm, prompt=summary_prompt_template)
    chain = summary_prompt_template | llm | summary_parser # LCEL, pipe
    res:Summary = chain.invoke(input={"information": linkedin_data})

    return res, linkedin_data.get("profile_pic_url")

if __name__ == "__main__":
    load_dotenv()
    
    print("Ice Breaker Enter")
    ice_break_with(name="Eden Marco Udemy")

