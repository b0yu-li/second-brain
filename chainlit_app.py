import os
import chainlit as cl
from src.brain import orchestrator_agent
from src.telemetry import init_telemetry
from main import load_memory, save_memory

# Initialize telemetry on startup
init_telemetry(project_name="second-brain-ui")


@cl.on_chat_start
async def start():
    """Initialize chat session with persistent memory."""
    chat_history = load_memory()
    cl.user_session.set("chat_history", chat_history)
    
    # Show knowledge base files
    data_files = [f for f in os.listdir("./data") if f.endswith((".txt", ".md"))]
    
    await cl.Message(
        content="🧠 **Second Brain is online!**\n\nI can search your knowledge base and remember our conversations. Ask me anything!",
    ).send()
    
    await cl.Message(
        content=f"📚 **Knowledge Base:** {', '.join(data_files) if data_files else 'No files found'}",
        author="System"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with visible researcher delegation."""
    chat_history = cl.user_session.get("chat_history", [])
    
    # Run agent with step tracking
    async with cl.Step(name="Orchestrator Agent", type="llm") as step:
        result = await orchestrator_agent.run(
            message.content, 
            message_history=chat_history
        )
        
        # Check if researcher was called
        tool_calls = [
            msg for msg in result.new_messages() 
            if hasattr(msg, 'parts') and any(
                hasattr(p, 'tool_name') and p.tool_name == 'consult_researcher' 
                for p in msg.parts
            )
        ]
        
        if tool_calls:
            step.output = "🔍 Delegated to Researcher Agent for knowledge base search"
        else:
            step.output = "💭 Answered from conversation memory"
    
    # Send response
    await cl.Message(content=result.output).send()
    
    # Update persistent memory
    chat_history = result.all_messages()
    cl.user_session.set("chat_history", chat_history)
    save_memory(chat_history)


@cl.on_chat_end
async def end():
    """Clean up when chat ends."""
    pass
