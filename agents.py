"""
Module for creating and managing research crews.

This module provides functionality for creating and configuring research crews,
which are composed of agents and tasks. It also includes tools for searching the web
and analyzing search results.

Classes:
    LinkUpSearchInput: Input schema for LinkUp Search Tool.
    LinkUpSearchTool: Tool for searching the web using LinkUp.
    Agent: Represents an agent in the research crew.
    Task: Represents a task in the research crew.
    Crew: Represents the research crew.

Functions:
    get_llm_client: Initializes and returns the Gemini LLM client.
    create_research_crew: Creates and configures the research crew.
    run_research: Runs the research process and returns results.
"""

import os
from typing import Type
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from linkup import LinkupClient
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool

# Load environment variables from .env file
load_dotenv()


def get_llm_client() -> LLM:
    """
    Initializes and returns the Gemini LLM client.

    Returns:
        LLM: The Gemini LLM client.
    """
    return LLM(
        model="gemini/gemini-2.5-flash",
        verbose=True,
        temperature=0.0,
        api_key=os.getenv("GEMINI_API_KEY")
    )


class LinkUpSearchInput(BaseModel):
    """
    Input schema for LinkUp Search Tool.

    Attributes:
        query (str): The search query to perform.
        depth (str): Depth of search: 'standard' or 'deep'. Defaults to 'standard'.
        output_type (str): Output type: 'searchResults', 'sourcedAnswer', or 'structured'. Defaults to 'searchResults'.
    """
    query: str = Field(description="The search query to perform")
    depth: str = Field(default="standard", description="Depth of search: 'standard' or 'deep'")
    output_type: str = Field(default="searchResults", description="Output type: 'searchResults', 'sourcedAnswer', or 'structured'")


class LinkUpSearchTool(BaseTool):
    """
    Tool for searching the web using LinkUp.

    Attributes:
        name (str): The name of the tool.
        description (str): The description of the tool.
        args_schema (Type[BaseModel]): The input schema for the tool.
    """
    name: str = "LinkUp Search"
    description: str = "Search the web for information using LinkUp and return comprehensive results"
    args_schema: Type[BaseModel] = LinkUpSearchInput

    def __init__(self):
        super().__init__()

    def _run(self, query: str, depth: str = "standard", output_type: str = "searchResults") -> str:
        """
        Execute LinkUp search and return results.

        Args:
            query (str): The search query to perform.
            depth (str): Depth of search: 'standard' or 'deep'. Defaults to 'standard'.
            output_type (str): Output type: 'searchResults', 'sourcedAnswer', or 'structured'. Defaults to 'searchResults'.

        Returns:
            str: The search results.
        """
        try:
            # Initialize LinkUp client with API key from environment variables
            linkup_client = LinkupClient(api_key=os.getenv("LINKUP_API_KEY"))

            # Perform search
            search_response = linkup_client.search(
                query=query,
                depth=depth,
                output_type=output_type
            )

            return str(search_response)
        except Exception as e:
            return f"Error occurred while searching: {str(e)}"


def create_research_crew(query: str) -> Crew:
    """
    Creates and configures the research crew.

    Args:
        query (str): The research query.

    Returns:
        Crew: The research crew.
    """
    # Initialize tools
    linkup_search_tool = LinkUpSearchTool()

    # Get LLM client
    client = get_llm_client()

    web_searcher = Agent(
        role="Web Searcher",
        goal=(
            "Locate the most authoritative, up-to-date, and relevant information on the web to comprehensively address the research query. "
            "Ensure all findings are accompanied by accurate source links (urls) suitable for citation in a formal research report. "
            "Gather data, facts, and potential visuals (charts, diagrams, images) that could support the report's sections: Executive Summary, Key Findings, Visuals, Conclusion, and References."
        ),
        backstory=(
            "A specialist in advanced web research, skilled at constructing precise queries and evaluating the credibility of sources. "
            "Responsible for assembling a robust set of resources and raw findings, with clear citations, to enable deep analysis and structured reporting. "
            "Passes all findings to the 'Research Analyst' for synthesis."
        ),
        verbose=True,
        allow_delegation=True,
        tools=[linkup_search_tool],
        llm=client,
    )

    # Define the research analyst
    research_analyst = Agent(
        role="Research Analyst",
        goal=(
            "Output two sections in markdown format:\n\n## Research Report\nPrepare structured notes for each section of the Research Report: Executive Summary, Key Findings, Visuals, Conclusion, and References.\n\n## Thinking Process Summary\nFor each key finding or section, explicitly explain which sources ([n]) contributed to each conclusion and how the information was combined, contrasted, or selected. Provide reasoning for each major point, mapping citations to synthesis decisions, and avoid general statements. This output will be passed to the technical_writer for final presentation."
        ),
        backstory=(
            "An expert at critical analysis, fact-checking, and synthesis. Skilled in transforming unstructured data into actionable insights and structured outlines. "
            "Responsible for ensuring the accuracy and depth of findings, and for organizing content to facilitate clear, impactful reporting. "
            "Passes an organized, section-ready synthesis to the 'Technical Writer'."
        ),
        verbose=True,
        allow_delegation=True,
        llm=client,
    )

    # Define the technical writer
    technical_writer = Agent(
        role="Technical Writer",
        goal=(
            "Produce two outputs, each clearly separated by markdown headers, with the Research Report first and the Thinking Process Summary second:\n\n"
            "## (1) Research Report\n"
            "A well-structured Research Report in markdown format, with clear section headers and citations/source links (urls). The report must include the following sections: "
            "1. Executive Summary (required): Brief overview of the research objective and outcome.\n"
            "2. Key Findings (optional): Concise insights with citations, formatted as numbered references (e.g., [1], [2], etc.), matching the numbers in the References section. Each citation should use a number that corresponds to a source in the References section.\n"
            "3. Visuals (optional): Only include this section if an actual visualization (such as an image, chart, diagram, or table) is generated and can be shown in the report. Do NOT include this section if only suggestions, descriptions, or hypothetical visuals are available. If no real visualization is produced, omit the Visuals section entirely.\n"
            "4. Conclusion (required): Summary of key takeaways and suggested next steps.\n"
            "5. References (required): A numbered list of all sources cited in the report. The numbering must correspond to the citation numbers used in the Key Findings section. Do NOT include 'Accessed [Current Date]' or any placeholder access date in the references; only include the source title, website, and URL.\n"
            "Ensure each section is clearly labeled and written in a professional, accessible style.\n\n"
            "## (2) Thinking Process Summary\n"
            "Present the detailed Thinking Process Summary provided by the research_analyst, which for each key finding or section, explicitly explains which sources ([n]) contributed to each conclusion and how the information was combined, contrasted, or selected. The summary should provide reasoning for each major point, mapping citations to synthesis decisions, and avoid general statements. The technical_writer should not invent or reinterpret the reasoning, but simply present both outputs clearly and professionally.\n"
            "1. Executive Summary (required): Brief overview of the research objective and outcome.\n"
            "2. Key Findings (optional): Concise insights with citations, formatted as numbered references (e.g., [1], [2], etc.), matching the numbers in the References section. Each citation should use a number that corresponds to a source in the References section.\n"
            "3. Visuals (optional): Only include this section if an actual visualization (such as an image, chart, diagram, or table) is generated and can be shown in the report. Do NOT include this section if only suggestions, descriptions, or hypothetical visuals are available. If no real visualization is produced, omit the Visuals section entirely.\n"
            "4. Conclusion (required): Summary of key takeaways and suggested next steps.\n"
            "5. References (required): A numbered list of all sources cited in the report. The numbering must correspond to the citation numbers used in the Key Findings section. Do NOT include 'Accessed [Current Date]' or any placeholder access date in the references; only include the source title, website, and URL.\n"
            "Ensure each section is clearly labeled and written in a professional, accessible style.\n"

        ),
        backstory=(
            "An expert at structuring and communicating complex research in a clear, engaging, and accessible way. "
            "Responsible for transforming the analyst's synthesis into a polished, comprehensive Research Report, with careful attention to structure, clarity, and citation."
        ),
        verbose=True,
        allow_delegation=False,
        llm=client,
    )

    # Define tasks
    search_task = Task(
        description=(
            f"Conduct an exhaustive web search for authoritative, up-to-date information about: {query}. "
            "Collect facts, data, and potential visuals (charts, diagrams, images) relevant to the research query. "
            "Ensure all findings are accompanied by accurate source links (urls) suitable for citation in a formal research report."
        ),
        agent=web_searcher,
        expected_output="Comprehensive raw search results, including sources (urls) and any relevant visuals.",
        tools=[linkup_search_tool]
    )

    analysis_task = Task(
        description=(
            "Analyze the raw search results, extract key findings, and verify facts. "
            "Organize insights, suggest visuals, and compile a list of references. "
            "Prepare structured notes for each section of the Research Report: Executive Summary, Key Findings, Visuals, Conclusion, and References."
        ),
        agent=research_analyst,
        expected_output="A section-ready synthesis with key findings, suggested visuals, and a comprehensive reference list, all with citations.",
        context=[search_task]
    )

    writing_task = Task(
        description=(
            "Write a well-structured Research Report in markdown format, based on the research analysis. "
            "The report must include the following sections: "
            "- Executive Summary (required): Brief overview of the research objective and outcome.\n"
            "- Key Findings (optional): Concise insights with citations if applicable.\n"
            "- Visuals (optional): Charts, diagrams, or images that support the findings.\n"
            "- Conclusion (required): Summary of key takeaways and suggested next steps.\n"
            "- References (required): List of sources used in the research.\n"
            "Ensure each section is clearly labeled and the writing is professional, clear, and accessible."
        ),
        agent=technical_writer,
        expected_output="A markdown-formatted Research Report with all required sections, clear structure, and citations/source links (urls).",
        context=[analysis_task]
    )

    # Create the crew
    crew = Crew(
        agents=[web_searcher, research_analyst, technical_writer],
        tasks=[search_task, analysis_task, writing_task],
        verbose=True,
        process=Process.sequential
    )

    return crew


def run_research(query: str) -> str:
    """
    Runs the research process and returns results.

    Args:
        query (str): The research query.

    Returns:
        str: The research results.
    """
    try:
        crew = create_research_crew(query)
        result = crew.kickoff()
        return result.raw
    except Exception as e:
        return f"Error: {str(e)}"
