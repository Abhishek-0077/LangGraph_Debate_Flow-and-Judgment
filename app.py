from langgraph.graph import StateGraph , START , END
from typing import TypedDict
import google.generativeai as genai

GENAI_API_KEY = "API"
genai.configure(api_key=GENAI_API_KEY)

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

class Agentstate(TypedDict):
  topic : str
  memory : str
  round : int
  response : str
  current_person : str
  Judgement : str


def user_node(state : Agentstate)->Agentstate:
  print('\nStarting debate between Scientist and Philosopher.....\n')

  state['round'] = 0
  state['memory'] = ""
  
  return state

def scientist(state : Agentstate)->Agentstate:
  """Add messege by scientist"""

  state['current_person'] = 'Scientist'
  state['round'] += 1

  prompt = f""" 
You are a Scientist debating the topic: {state['topic']}".
Here is your memory: {state['memory']}
This is your round {state['round']}. Be concise and logical. State your argument clearly. in just 2 lines 
"""

  state['response'] = model.generate_content(prompt).text.strip()
 
  return state

def memory_node(state : Agentstate)->Agentstate:
  """Save in memory"""

  messege = f"[Round {state['round']}] {state['current_person']} : {state['response']}\n"
  print(messege)
  state['memory'] += messege
  
  return state


def philosopher(state:Agentstate)->Agentstate:
  """Add messege by Philosopher"""
  
  state['current_person'] = 'Philosopher'
  state['round'] += 1
  
  prompt = f""" 
You are a Philosopher debating the topic: {state['topic']}".
Here is your memory: {state['memory']}
This is your round #{state['round']}. Be concise and logical. State your argument clearly. in just 2 lines 
"""
    
  state['response'] = model.generate_content(prompt).text.strip()
  
  return state

def check(state : Agentstate)->str:
  if(state['round'] == 8):
    with open("log.txt", "a") as f:
      f.write(f"Debate topic : {state['topic']}\n")
      f.write(f"{state['memory']}")

    return "Judge"
  if(state["current_person"]=='Scientist'):
    return 'Philosopher'
  return 'Scientist'


def judge(state:Agentstate)->Agentstate:
  """make Judgement"""
  conversation = state['memory']

  prompt = f"""
You are the Judge of a debate on the topic: {topic}".

Here is the full transcript:
{conversation}

1. Summarize each participant's core points.
2. Evaluate the logical structure, evidence, and depth of argument.
3. Declare the winner and provide justification.
Remember it cann't be a tie......

Format:
Summary:
- Scientist: ...
- Philosopher: ...

Evaluation:

Winner: [Scientist/Philosopher]
Reason: ...
"""

  result = model.generate_content(prompt).text.strip()
  temp = f"[judge] {result}"
  print(temp)
  state["Judgement"] = temp
  with open("log.txt", "a") as f:
      f.write(f"{state['Judgement']}\n")
  return state



graph = StateGraph(Agentstate)

graph.add_node("User_node",user_node)
graph.add_node("Scientist",scientist)
graph.add_node("Philosopher",philosopher)
graph.add_node("Judge",judge)
graph.add_node("Memory",memory_node)

graph.add_edge(START,"User_node")
graph.add_edge("User_node","Scientist")
graph.add_edge("Scientist" , "Memory")
graph.add_edge("Philosopher" , "Memory")

graph.add_conditional_edges("Memory",check , {
    "Philosopher": "Philosopher",
    "Scientist": "Scientist",
    "Judge": "Judge"
})


graph.add_edge("Judge",END)
app = graph.compile()

if __name__ == "__main__":
    topic = input("Enter debate topic: ")
    app.invoke({'topic':topic})
