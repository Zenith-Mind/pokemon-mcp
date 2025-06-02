from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

app = FastAPI(title="Pokemon MCP Web Interface")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq LLM
if os.getenv('GROQ_API_KEY'):
    llm = ChatGroq(
        model="qwen-qwq-32b",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    print("Using Groq with Qwen-qwq-32b")
else:
    print('Export GROQ_API_KEY to initialize Qwen LLM.')
    print('Get your API key from: https://console.groq.com/')
    exit(1)

# Initialize MCP client
mcp_client = MultiServerMCPClient({
    "pokemon_server": {
        "url": os.getenv("POKEMON_MCP_URL", "http://localhost:8000/sse"),
        "transport": "sse"
    }
})

# Create agent
agent = None

async def initialize_agent():
    global agent
    tools = await mcp_client.get_tools()
    print("Loaded Pokémon MCP tools: " + ", ".join(tool.name for tool in tools))
    
    agent = create_react_agent(
        llm,
        tools=tools,
        prompt="""You are a Pokémon expert assistant. You have access to tools that can:
        - Get detailed information about any Pokémon
        - Compare two Pokémon's attributes  
        - Analyze type matchups and strategies
        - Suggest balanced team compositions

        Use these tools to provide comprehensive and helpful responses about Pokémon.
        Always use the available tools when you need information about specific Pokémon.
        Don't ask follow-up questions, only use the tools.
        
        Format your responses in a clear, README-style format:
        - Use markdown headers (##) for main sections
        - Use bullet points for lists
        - Use tables for comparisons
        - Use code blocks for detailed stats
        - Use bold for important information
        - Keep responses concise but informative
        - Structure information in a logical flow
        - Use emojis sparingly for visual appeal"""
    )

@app.on_event("startup")
async def startup_event():
    await initialize_agent()

async def process_query(query: str) -> str:
    """Process a query using the MCP agent."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        agent_response = await agent.ainvoke({"messages": query})
        return agent_response['messages'][-1].content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/query/{tool_name}")
async def handle_query(tool_name: str, params: Dict[str, Any]):
    """Handle queries for specific tools."""
    if tool_name not in ["get_pokemon", "compare_pokemon", "get_type_matchups", "suggest_team"]:
        raise HTTPException(status_code=400, detail="Invalid tool name")
    
    # Construct a natural language query based on the tool and parameters
    query = ""
    if tool_name == "get_pokemon":
        query = f"Tell me about {params.get('name', '')}"
    elif tool_name == "compare_pokemon":
        query = f"Compare {params.get('pokemon1', '')} and {params.get('pokemon2', '')}"
    elif tool_name == "get_type_matchups":
        query = f"What are the type matchups for {params.get('pokemon_name', '')}?"
    elif tool_name == "suggest_team":
        query = f"Suggest a team based on this description: {params.get('description', '')}"
    
    response = await process_query(query)
    return {"response": response}

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the web interface."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pokemon MCP Interface</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.0/github-markdown.min.css">
        <style>
            :root {
                --primary-color: #4CAF50;
                --primary-hover: #45a049;
                --background-color: #f5f7fa;
                --card-background: #ffffff;
                --text-color: #333333;
                --border-color: #e1e4e8;
                --shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: 'Poppins', sans-serif;
                background-color: var(--background-color);
                color: var(--text-color);
                line-height: 1.6;
                padding: 20px;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }

            header {
                text-align: center;
                margin-bottom: 40px;
                padding: 20px;
                background: var(--card-background);
                border-radius: 10px;
                box-shadow: var(--shadow);
            }

            h1 {
                color: var(--primary-color);
                font-size: 2.5em;
                margin-bottom: 10px;
            }

            .subtitle {
                color: #666;
                font-size: 1.1em;
            }

            .tools-grid {
                display: flex;
                flex-direction: column;
                gap: 40px;
                margin-top: 20px;
                max-width: 900px;
                margin-left: auto;
                margin-right: auto;
            }

            .tool-section {
                background: var(--card-background);
                padding: 30px;
                border-radius: 10px;
                box-shadow: var(--shadow);
                transition: transform 0.2s ease;
                width: 100%;
            }

            .tool-section:hover {
                transform: translateY(-5px);
            }

            .tool-section h2 {
                color: var(--primary-color);
                margin-bottom: 25px;
                font-size: 1.8em;
                border-bottom: 2px solid var(--border-color);
                padding-bottom: 15px;
            }

            .input-group {
                margin: 20px 0;
                max-width: 600px;
            }

            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #555;
            }

            input, textarea {
                width: 100%;
                padding: 14px;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                font-size: 1.1em;
                transition: all 0.3s ease;
                background-color: #fafafa;
            }

            input:focus, textarea:focus {
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
                background-color: #ffffff;
            }

            button {
                background: var(--primary-color);
                color: white;
                border: none;
                padding: 14px 28px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1.1em;
                font-weight: 500;
                transition: all 0.3s ease;
                width: 100%;
                margin-top: 15px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            button:hover {
                background: var(--primary-hover);
                transform: translateY(-1px);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            button:active {
                transform: translateY(0);
            }

            .response-box {
                background: #ffffff;
                padding: 25px;
                border-radius: 8px;
                margin-top: 25px;
                border: 1px solid var(--border-color);
                min-height: 150px;
                max-height: 800px;
                overflow-y: auto;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
            }

            .response-box.markdown-body {
                font-size: 15px;
                line-height: 1.7;
            }

            .response-box.markdown-body h1 {
                font-size: 1.8em;
                margin-top: 0;
                padding-top: 20px;
            }

            .response-box.markdown-body h2 {
                font-size: 1.5em;
                margin-top: 30px;
                border-bottom: none;
                padding-bottom: 0;
            }

            .response-box.markdown-body h3 {
                font-size: 1.3em;
                margin-top: 25px;
            }

            .response-box.markdown-body p {
                margin: 15px 0;
            }

            .response-box.markdown-body ul, 
            .response-box.markdown-body ol {
                margin: 15px 0;
                padding-left: 25px;
            }

            .response-box.markdown-body li {
                margin: 8px 0;
            }

            .response-box.markdown-body table {
                margin: 20px 0;
                font-size: 0.95em;
            }

            .response-box.markdown-body code {
                font-size: 0.9em;
                padding: 0.2em 0.4em;
            }

            .response-box.markdown-body pre {
                margin: 20px 0;
                padding: 20px;
            }

            .loading {
                display: none;
                text-align: center;
                margin: 15px 0;
                color: #666;
                font-size: 1.1em;
            }

            .loading::after {
                content: '';
                display: inline-block;
                width: 24px;
                height: 24px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid var(--primary-color);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-left: 12px;
                vertical-align: middle;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .error {
                color: #dc3545;
                background: #f8d7da;
                padding: 12px 15px;
                border-radius: 8px;
                margin-top: 15px;
                display: none;
                font-size: 1.1em;
                border: 1px solid #f5c6cb;
            }

            @media (max-width: 768px) {
                .tools-grid {
                    padding: 0 15px;
                }
                
                .tool-section {
                    padding: 20px;
                }
                
                .response-box {
                    padding: 20px;
                }
            }

            /* Add a subtle separator between sections */
            .tool-section:not(:last-child)::after {
                content: '';
                display: block;
                height: 1px;
                background: var(--border-color);
                margin: 40px 0 0 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Pokemon MCP Interface</h1>
                <p class="subtitle">Your Pokemon assistant</p>
            </header>

            <div class="tools-grid">
                <div class="tool-section">
                    <h2>Get Pokemon Info</h2>
                    <div class="input-group">
                        <label for="pokemon-name">Pokemon Name:</label>
                        <input type="text" id="pokemon-name" placeholder="e.g., Pikachu">
                        <button onclick="getPokemon()">Get Info</button>
                        <span id="pokemon-loading" class="loading">Processing...</span>
                        <div id="pokemon-error" class="error"></div>
                    </div>
                    <div id="pokemon-response" class="response-box markdown-body"></div>
                </div>

                <div class="tool-section">
                    <h2>Compare Pokemon</h2>
                    <div class="input-group">
                        <label for="pokemon1">First Pokemon:</label>
                        <input type="text" id="pokemon1" placeholder="e.g., Charizard">
                        <label for="pokemon2">Second Pokemon:</label>
                        <input type="text" id="pokemon2" placeholder="e.g., Blastoise">
                        <button onclick="comparePokemon()">Compare</button>
                        <span id="compare-loading" class="loading">Processing...</span>
                        <div id="compare-error" class="error"></div>
                    </div>
                    <div id="compare-response" class="response-box markdown-body"></div>
                </div>

                <div class="tool-section">
                    <h2>Get Type Matchups</h2>
                    <div class="input-group">
                        <label for="matchup-pokemon">Pokemon Name:</label>
                        <input type="text" id="matchup-pokemon" placeholder="e.g., Mewtwo">
                        <button onclick="getTypeMatchups()">Get Matchups</button>
                        <span id="matchup-loading" class="loading">Processing...</span>
                        <div id="matchup-error" class="error"></div>
                    </div>
                    <div id="matchup-response" class="response-box markdown-body"></div>
                </div>

                <div class="tool-section">
                    <h2>Suggest Team</h2>
                    <div class="input-group">
                        <label for="team-description">Team Description:</label>
                        <textarea id="team-description" rows="3" placeholder="e.g., balanced team with strong defense and fire attacker"></textarea>
                        <button onclick="suggestTeam()">Suggest Team</button>
                        <span id="team-loading" class="loading">Processing...</span>
                        <div id="team-error" class="error"></div>
                    </div>
                    <div id="team-response" class="response-box markdown-body"></div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script>
            async function makeRequest(endpoint, params, loadingId, responseId, errorId) {
                const loading = document.getElementById(loadingId);
                const response = document.getElementById(responseId);
                const error = document.getElementById(errorId);
                
                try {
                    loading.style.display = 'inline';
                    response.textContent = '';
                    error.style.display = 'none';
                    
                    const result = await fetch(`/query/${endpoint}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(params)
                    });
                    
                    if (!result.ok) {
                        throw new Error(`HTTP error! status: ${result.status}`);
                    }
                    
                    const data = await result.json();
                    response.innerHTML = marked.parse(data.response);
                } catch (error) {
                    const errorElement = document.getElementById(errorId);
                    errorElement.textContent = 'Error: ' + error.message;
                    errorElement.style.display = 'block';
                } finally {
                    loading.style.display = 'none';
                }
            }

            async function getPokemon() {
                const pokemonName = document.getElementById('pokemon-name').value;
                if (!pokemonName) {
                    const error = document.getElementById('pokemon-error');
                    error.textContent = 'Please enter a Pokemon name';
                    error.style.display = 'block';
                    return;
                }
                await makeRequest('get_pokemon', { name: pokemonName }, 'pokemon-loading', 'pokemon-response', 'pokemon-error');
            }

            async function comparePokemon() {
                const pokemon1 = document.getElementById('pokemon1').value;
                const pokemon2 = document.getElementById('pokemon2').value;
                if (!pokemon1 || !pokemon2) {
                    const error = document.getElementById('compare-error');
                    error.textContent = 'Please enter both Pokemon names';
                    error.style.display = 'block';
                    return;
                }
                await makeRequest('compare_pokemon', { pokemon1, pokemon2 }, 'compare-loading', 'compare-response', 'compare-error');
            }

            async function getTypeMatchups() {
                const pokemonName = document.getElementById('matchup-pokemon').value;
                if (!pokemonName) {
                    const error = document.getElementById('matchup-error');
                    error.textContent = 'Please enter a Pokemon name';
                    error.style.display = 'block';
                    return;
                }
                await makeRequest('get_type_matchups', { pokemon_name: pokemonName }, 'matchup-loading', 'matchup-response', 'matchup-error');
            }

            async function suggestTeam() {
                const description = document.getElementById('team-description').value;
                if (!description) {
                    const error = document.getElementById('team-error');
                    error.textContent = 'Please enter a team description';
                    error.style.display = 'block';
                    return;
                }
                await makeRequest('suggest_team', { description }, 'team-loading', 'team-response', 'team-error');
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 