from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
import logging

logger = logging.getLogger("modular-2")

class LLMConfig(BaseModel):
    name: Optional[str] = None  # Nome identificativo del provider
    provider: str
    model: str
    endpoint: Optional[HttpUrl] = None
    api_key: Optional[str] = None

class ToolConfig(BaseModel):
    name: str
    class_path: str
    config: Optional[dict] = Field(default_factory=dict)

class AgentConfig(BaseModel): 
    name: str
    llm: Optional[str] = None
    tools: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    type: Optional[str] = "simple"

class RetrieverConfig(BaseModel):
    name: str
    class_path: str
    config: Optional[dict] = Field(default_factory=dict)

class MemoryConfig(BaseModel):
    name: str
    class_path: str
    config: Optional[dict] = Field(default_factory=dict)

class DocumentLoaderConfig(BaseModel):
    name: str
    class_path: str
    config: Optional[dict] = Field(default_factory=dict)

class TextSplitterConfig(BaseModel):
    name: str
    class_path: str
    config: Optional[dict] = Field(default_factory=dict)

class EvaluatorConfig(BaseModel):
    name: str
    class_path: str
    config: Optional[dict] = Field(default_factory=dict)

class OutputParserConfig(BaseModel):
    name: str
    class_path: str
    config: Optional[dict] = Field(default_factory=dict)

class ChainStepConfig(BaseModel):
    name: str
    type: str  # e.g. 'llm', 'tool', 'agent', 'retriever', 'memory', 'splitter', 'evaluator', 'parser', 'chain', 'condition', 'fallback'
    component: str  # name/id of the component to use
    input: Optional[dict] = None  # input mapping/vars
    output: Optional[str] = None  # output var name
    condition: Optional[str] = None  # python expr or yaml logic
    fallback: Optional[str] = None  # fallback step/component
    on_error: Optional[str] = None  # error handler
    tracing: Optional[bool] = True
    params: Optional[dict] = None

class ChainConfig(BaseModel):
    name: str
    steps: List[ChainStepConfig]
    description: Optional[str] = None
    tracing: Optional[bool] = True

class PipelineConfig(BaseModel):
    name: str
    chains: List[ChainConfig]
    description: Optional[str] = None
    tracing: Optional[bool] = True

class Config(BaseModel):
    llms: Optional[List[LLMConfig]] = None  # Supporto multi-provider
    llm: Optional[LLMConfig] = None  # Per retrocompatibilità (singolo provider)
    tools: Optional[List[ToolConfig]] = None
    agents: Optional[List[AgentConfig]] = None
    retrievers: Optional[List[RetrieverConfig]] = None
    memory: Optional[List[MemoryConfig]] = None
    document_loaders: Optional[List[DocumentLoaderConfig]] = None
    splitters: Optional[List[TextSplitterConfig]] = None
    evaluators: Optional[List[EvaluatorConfig]] = None
    output_parsers: Optional[List[OutputParserConfig]] = None
    chains: Optional[List[ChainConfig]] = None
    pipelines: Optional[List[PipelineConfig]] = None
