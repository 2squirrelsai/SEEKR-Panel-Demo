"""
CrewAI agent definitions and orchestration.

Defines specialized agents for customer service query handling:
- Query Analyzer: Classifies and understands customer queries
- Policy Retrieval Agent: Searches for relevant policy information
- Response Generator: Crafts helpful, accurate customer responses
"""

import logging
from typing import List
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

logger = logging.getLogger("ecom_cs_agent.agents")


class CustomerServiceCrew:
    """
    Orchestrates a crew of specialized agents for customer service automation.

    The crew works together to analyze queries, retrieve policy information,
    and generate helpful responses to customer questions.
    """

    def __init__(
        self,
        llm_model: str,
        api_key: str,
        tools: List,
        verbose: bool = False
    ):
        """
        Initialize the customer service crew.

        Args:
            llm_model: OpenAI model name
            api_key: OpenAI API key
            tools: List of tools available to agents
            verbose: Enable verbose output
        """
        self.llm = ChatOpenAI(
            model=llm_model,
            api_key=api_key,
            temperature=0.3  # Lower temperature for more consistent responses
        )
        self.tools = tools
        self.verbose = verbose

        # Create agents
        self.query_analyzer = self._create_query_analyzer()
        self.policy_retriever = self._create_policy_retriever()
        self.response_generator = self._create_response_generator()

        logger.info("Customer service crew initialized with 3 agents")

    def _create_query_analyzer(self) -> Agent:
        """
        Create the Query Analyzer agent.

        This agent understands customer queries, identifies intent,
        and extracts key information like product categories and dates.
        """
        return Agent(
            role="Customer Query Analyzer",
            goal=(
                "Analyze customer queries to understand their needs, identify the type of request "
                "(return, refund, exchange, policy question), and extract relevant details like "
                "product information, purchase dates, and specific concerns."
            ),
            backstory=(
                "You are an expert customer service analyst with years of experience understanding "
                "customer needs in eCommerce. You excel at reading between the lines to identify "
                "what customers truly need, even when they don't express it clearly. You have a "
                "keen eye for details like dates, product types, and the emotional tone of queries."
            ),
            llm=self.llm,
            verbose=self.verbose,
            allow_delegation=False
        )

    def _create_policy_retriever(self) -> Agent:
        """
        Create the Policy Retrieval agent.

        This agent searches the knowledge base for relevant policies,
        calculates return eligibility, and summarizes policy information.
        """
        return Agent(
            role="Policy Retrieval Specialist",
            goal=(
                "Search the policy knowledge base for accurate, relevant information about returns, "
                "refunds, timeframes, and procedures. Calculate return eligibility based on dates "
                "and policies. Provide clear, factual policy information."
            ),
            backstory=(
                "You are a meticulous policy expert who knows every detail of the company's return "
                "and refund policies. You have access to comprehensive policy documents and tools "
                "to verify eligibility. You never guess - you always consult the official policies "
                "and use calculators to provide accurate information. Your responses are always "
                "backed by concrete policy references."
            ),
            llm=self.llm,
            tools=self.tools,  # Policy retriever has access to all tools
            verbose=self.verbose,
            allow_delegation=False
        )

    def _create_response_generator(self) -> Agent:
        """
        Create the Response Generator agent.

        This agent crafts helpful, empathetic, and accurate responses
        to customer queries based on policy information.
        """
        return Agent(
            role="Customer Response Specialist",
            goal=(
                "Generate clear, empathetic, and helpful responses to customer queries. Provide "
                "accurate policy information, step-by-step instructions when needed, and maintain "
                "a professional yet friendly tone. Always prioritize customer satisfaction while "
                "adhering to company policies."
            ),
            backstory=(
                "You are a seasoned customer service representative known for your exceptional "
                "communication skills. You have a gift for explaining complex policies in simple "
                "terms that customers can easily understand. You are empathetic and always put "
                "yourself in the customer's shoes, while maintaining professionalism and accuracy. "
                "You know when to be firm about policies and when to offer alternative solutions."
            ),
            llm=self.llm,
            verbose=self.verbose,
            allow_delegation=False
        )

    def process_query(self, customer_query: str) -> str:
        """
        Process a customer query through the agent crew.

        Args:
            customer_query: The customer's question or concern

        Returns:
            Final response to the customer
        """
        logger.info(f"Processing query: '{customer_query[:50]}...'")

        # Task 1: Analyze the query
        analyze_task = Task(
            description=(
                f"Analyze this customer query and identify:\n"
                f"1. Type of request (return, refund, exchange, policy question)\n"
                f"2. Product category if mentioned\n"
                f"3. Any dates mentioned (purchase date, current situation)\n"
                f"4. Specific concerns or questions\n"
                f"5. Emotional tone (frustrated, confused, neutral)\n\n"
                f"Customer Query: {customer_query}"
            ),
            expected_output=(
                "A structured analysis including request type, product details, dates, "
                "key concerns, and recommended approach for handling this query."
            ),
            agent=self.query_analyzer
        )

        # Task 2: Retrieve relevant policies
        retrieve_task = Task(
            description=(
                "Based on the query analysis, retrieve relevant policy information:\n"
                "1. Use the policy search tool to find relevant documents\n"
                "2. If dates are mentioned, calculate return eligibility\n"
                "3. Summarize key policy points that apply to this situation\n"
                "4. Identify any special cases or exceptions\n\n"
                "Provide factual, policy-based information that will help answer the query."
            ),
            expected_output=(
                "Relevant policy information, eligibility status (if applicable), "
                "key requirements, timeframes, and any important conditions or exceptions."
            ),
            agent=self.policy_retriever,
            context=[analyze_task]
        )

        # Task 3: Generate customer response
        response_task = Task(
            description=(
                "Create a helpful response to the customer based on the query analysis "
                "and policy information:\n"
                "1. Address the customer's specific question directly\n"
                "2. Explain relevant policies in clear, simple language\n"
                "3. Provide step-by-step instructions if applicable\n"
                "4. Include important dates, deadlines, or requirements\n"
                "5. Offer alternative solutions if the primary request cannot be fulfilled\n"
                "6. Maintain an empathetic and professional tone\n\n"
                "The response should be complete, accurate, and helpful."
            ),
            expected_output=(
                "A complete customer service response that directly answers the query, "
                "explains relevant policies, provides clear next steps, and maintains "
                "a professional yet empathetic tone."
            ),
            agent=self.response_generator,
            context=[analyze_task, retrieve_task]
        )

        # Create and execute the crew
        crew = Crew(
            agents=[self.query_analyzer, self.policy_retriever, self.response_generator],
            tasks=[analyze_task, retrieve_task, response_task],
            process=Process.sequential,
            verbose=self.verbose
        )

        logger.info("Starting crew execution")
        result = crew.kickoff()

        logger.info("Query processing completed")
        return str(result)


def create_customer_service_crew(
    llm_model: str,
    api_key: str,
    tools: List,
    verbose: bool = False
) -> CustomerServiceCrew:
    """
    Factory function to create a customer service crew.

    Args:
        llm_model: OpenAI model name
        api_key: OpenAI API key
        tools: List of tools for agents
        verbose: Enable verbose output

    Returns:
        Configured CustomerServiceCrew instance
    """
    return CustomerServiceCrew(
        llm_model=llm_model,
        api_key=api_key,
        tools=tools,
        verbose=verbose
    )
