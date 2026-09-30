import sys, os

sys.path.insert( 0, os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )

from deepeval.evaluate import evaluate
from deepeval.metrics import TurnRelevancyMetric, KnowledgeRetentionMetric, ConversationCompletenessMetric
from deepeval.test_case import ConversationalTestCase, Turn
from llm_models import LLMModel


from chatbot import chat

turns = []
history = []
for user_msg in [
        "Hi! I placed an order last week, the order ID is ORD-1042.",

        "Is it going to arrive on time?",
        "What was the ETA you just mentioned?",   # tests memory retention
        "Can I upgrade to express shipping?",
    ]:
       reply,history, _  = chat(user_msg,history)
       print(f"User: {user_msg}\nAssistant: {reply}\n")
       turns.append(Turn(role="user",content=user_msg))
       turns.append(Turn(role="assistant",content=reply))

turnRelevancyMetric = TurnRelevancyMetric(threshold=0.5, model=LLMModel.GPT_OSS)
retentionMetric = KnowledgeRetentionMetric(threshold=0.5, model=LLMModel.GPT_OSS)
completnessMetric = ConversationCompletenessMetric(threshold=0.5, model=LLMModel.GPT_OSS)

test_case = ConversationalTestCase(
    turns = turns
)

evaluate(test_cases = [test_case], metrics = [turnRelevancyMetric,retentionMetric,completnessMetric])