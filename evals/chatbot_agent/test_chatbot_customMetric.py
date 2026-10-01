import sys, os

sys.path.insert( 0, os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) ) )

os.environ.setdefault("DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE", "900")
os.environ.setdefault("DEEPEVAL_PER_ATTEMPT_TIMEOUT_SECONDS_OVERRIDE", "300")

from deepeval.evaluate import evaluate
from deepeval.metrics import GEval, ConversationalGEval
from deepeval.test_case import Turn, ConversationalTestCase, MultiTurnParams

from chatbot import chat
from llm_models import LLMModel

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

correctness = ConversationalGEval(
    name = "Correctness",
    criteria=(
         "Did the chatbot fully resolve the customer's issue? "
      "It should use tools when needed and provide accurate answers."
    ),
    model=LLMModel.GPT_OSS,
    threshold=0.80,
    evaluation_params=[
        MultiTurnParams.ROLE,
        MultiTurnParams.CONTENT,
         ])


test_case = ConversationalTestCase(
    turns = turns
)

evaluate(test_cases = [test_case], metrics = [correctness])