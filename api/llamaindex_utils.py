import os
import chromadb
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex, StorageContext,
    get_response_synthesizer, PromptTemplate
)
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.postprocessor import MetadataReplacementPostProcessor, SimilarityPostprocessor
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import Settings

# Configuration
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

AIRLINES = [
    "Delta", "AmericanAirlines", "UnitedAirlines",
    "Southwest", "HawaiianAirlines", "frontier",
    "Spicejet", "Airindia", "AkasaAir"
]

# Initialize components
Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Response templates (same as provided)
text_qa_template = PromptTemplate(""""Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Your task is to provide a **detailed, structured answer** that includes:\n"
    "- All relevant rules, exceptions, and limitations.\n"
    "- Bullet points or numbered lists for clarity.\n"
    "- Links to resources (if present in the context).\n"
    "- Examples from the context where applicable.\n\n"
    "Query: {query_str}\n"
    "Answer in the following format:\n"
    "1. **Main Answer**: [Concise summary]\n"
    "2. **Details**:\n"
    "   - Subpoints with specifics (regions, limits, etc.)\n"
    "3. **Exceptions/Notes**: [Any restrictions or edge cases]\n"
    "4. **Resources**: [Relevant links from the context]\n\n"
    "Answer:" """)

refine_template = PromptTemplate("""The original query is: {query_str}\n"
    "Existing Answer: {existing_answer}\n"
    "New Context: {context_msg}\n"
    "---------------------\n"
    "Refine the answer by:\n"
    "1. Adding missing details from the new context.\n"
    "2. Expanding examples or rules.\n"
    "3. Including exceptions/links if omitted earlier.\n"
    "4. Maintaining the structured format.\n\n"
    "If the new context is irrelevant, return the original answer.\n"
    "Refined Answer:""")


def initialize_system():
    chroma_client = chromadb.PersistentClient(path="../chroma_db")

    
    # Create query engines for all airlines
    response_synthesizer = get_response_synthesizer(
        response_mode="tree_summarize",
        text_qa_template=text_qa_template,
        refine_template=refine_template,
        llm=Settings.llm
    )
    
    tools = []
    for airline in AIRLINES:
        collection = chroma_client.get_collection(f"index_{airline}")
        vector_store = ChromaVectorStore(collection)
        
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=StorageContext.from_defaults(vector_store=vector_store)
        )
        
        query_engine = index.as_query_engine(
            response_synthesizer=response_synthesizer,
            node_postprocessors=[
                MetadataReplacementPostProcessor(target_metadata_key="window"),
                SimilarityPostprocessor(similarity_cutoff=0.3)
            ],
            similarity_top_k=4
        )
        
        tools.append(QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name=airline.lower(),
                description=f"{airline} policy analyzer"
            )
        ))
    
    return OpenAIAgent.from_tools(
        tools=tools,
        llm=Settings.llm,
        system_prompt = """Policy analysis assistant with structured responses.
                        Only answer using information from the provided context, unless it's a greeting message or thank you message.
                        If no relevant information is found, respond with 
                        'I cannot find relevant information to answer this question.'""",
        verbose=True
    )
