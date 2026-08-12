import warnings
warnings.filterwarnings("error")

try:
    from langgraph.prebuilt import create_react_agent
    print("imported from langgraph.prebuilt")
except Exception as e:
    print("error importing from langgraph.prebuilt:", e)

try:
    from langchain.agents import create_react_agent
    print("imported from langchain.agents")
except Exception as e:
    print("error importing from langchain.agents:", e)
