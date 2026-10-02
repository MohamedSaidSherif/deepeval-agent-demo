from dotenv import load_dotenv
load_dotenv()  # loads .env (incl. DeepEval timeout overrides) before deepeval import

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from deepeval.evaluate import evaluate
from deepeval.metrics import TaskCompletionMetric
from deepeval.test_case import LLMTestCase

from agent_instrumented import support_agent
from llm_models import LLMModel

user_input = "Where is my order ORD-1042?"
actual_output = support_agent(user_input)

test_case = LLMTestCase(
    input = user_input,
    actual_output = actual_output
)

evaluate(test_cases = [test_case],
         metrics= [TaskCompletionMetric(threshold=0.7,model = LLMModel.GPT_OSS)])