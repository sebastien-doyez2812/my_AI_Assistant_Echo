from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
import wikipediaapi

class ReasearchAgent:
    """
    DEF:
    ----
    The research agent will do some research on Wikipedia
    
    """
    def __init__(self, llm):
        self.llm = llm
        self.memory = ConversationBufferMemory(memory_key= "chat_history")

        self.tools = [
            Tool(
                name= "Wikipedia",
                func = self.search_wikipedia,
                description= "Useful for searching Wikipedia articles"
            ),
            Tool(
                name = "Calculator",
                func = self.calculate,
                description="Useful for performing mathematical calculations"
            )
        ]

        self.agent = initialize_agent(
            self.tools,
            llm= llm,
            agent = "zero-shot-react-description",
            verbose = True,
            memory = self.memory
        )

    def search_wikipedia(self, query):
        user_agent_wikipedia = "JarvisPython/1.0 (https://github.com/sebastien-doyez2812/AI-projects/AI_ChatBot)"
        wiki = wikipediaapi.Wikipedia(user_agent_wikipedia, 'fr')
        return wiki.page(query)
    
    def calculate(self, expression):
        return eval(expression)
    
    def run(self, query):
        return self.agent.run(query)
    

class AnalyticalAgent:
    """
    DEF:
    ----
    Give us a plan how to analyse the situation
    """
    def __init__(self, llm):
        self.llm = llm
        self.reasoning_prompt1 = PromptTemplate(
            input_variables= ["question"],
            template= """
        Question : {question}

        Let's approach this step by step:
        1) First, let's understand what we're being asked
        2) Then, let's identify the tools we need
        3) Finally, let's execute the plan 

        Reasoning and make an answer in 30 words:
        """
        )
        self.reasoning_chain = LLMChain(
            llm = self.llm,
            prompt = self.reasoning_prompt1
        )

    def analyse(self, question):
        reasoning = self.reasoning_chain.run(question)
        return {
            "reasoning": reasoning,
            "answer": "Final answer with less tthan 25 words based on analysis"
        }

class MultiAgentSystem:
    def __init__(self, llm):
        self.llm = llm
        self.reasearcher = ReasearchAgent(llm)
        self.analyzer = AnalyticalAgent(llm)

        # To do a multiagent system, we need to have a coordinator prompt
        self.coornator_prompt = PromptTemplate(
            input_variables= ["task"],
            template="""
            Task: {task}

            This task requires coordination between research and analysis.
            
            Plan:
            1) Research Phase:
               - What information do we need?
               - What sources should we consult?
            
            2) Analysis Phase:
               - How should we process the information?
               - What insights should we look for?
            
            3) Synthesis:
               - How do we combine the findings?
               - What conclusions can we draw?
            
            Let's proceed step by step.
            """
        )

        self.coordinator_chain = LLMChain(
            llm = self.llm,
            prompt= self.coornator_prompt
        )
    
    def execute_task(self, task):
        plan = self.coordinator_chain.run(task)
        
        research_task = f"Do a research using this plan: {plan}"

        research = self.reasearcher.run(research_task)

        analysis_task = f"Do an analysis with those results: {research}"

        analysis = self.analyzer.run(analysis_task)

        return {
            "output": analysis
        }

# Multiagent:
my_llm = OllamaLLM(model="gemma", prompt= "You are a useful AI agent, you give answer to question in less than 25 words.")
multi_agent_system = MultiAgentSystem(my_llm)