import asyncio
import json
import sys
from typing import Any, Dict, Optional
from modules.info_retrieval import InfoRetrievalModule
from modules.comparison import ComparisonModule
from modules.strategy import StrategyModule
from modules.team_composition import TeamCompositionModule
from modules.logger import ServerLogger

class PokemonMCPServer:
    def __init__(self):
        self.info_module = InfoRetrievalModule()
        self.comparison_module = ComparisonModule()
        self.strategy_module = StrategyModule()
        self.team_module = TeamCompositionModule()
        self.logger = ServerLogger()
        
    def validate_request(self, request: Dict[str, Any]) -> tuple[bool, str]:
        """Validate the incoming request structure."""
        if not isinstance(request, dict):
            return False, "Request must be a JSON object"
        
        if "query" not in request:
            return False, "Request must contain a 'query' field"
        
        if not isinstance(request["query"], str):
            return False, "Query must be a string"
        
        return True, ""
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        try:
            # Validate request structure
            is_valid, error_msg = self.validate_request(request)
            if not is_valid:
                self.logger.log_error(ValueError(error_msg), "Invalid request structure")
                return {"error": error_msg}
            
            query = request.get("query", "").strip()
            user = request.get("user", "unknown")
            
            # Log the incoming query
            self.logger.log_query(query, user)
            self.logger.log_server_activity(f"Processing query: {query}")
            
            if not query:
                return {"error": "No query provided"}
            
            # Parse the query
            parts = query.lower().split()
            command = parts[0]
            args = parts[1:]
            
            # Handle different commands
            if command == "get" and len(args) >= 2 and args[0] == "info":
                pokemon_name = " ".join(args[1:])
                result = await self.info_module.get_pokemon_info(pokemon_name)
            elif command == "compare" and len(args) >= 2:
                result = await self.comparison_module.compare_pokemon(args)
            elif command == "strategy" and len(args) >= 1:
                pokemon_name = " ".join(args)
                result = await self.strategy_module.get_type_matchups(pokemon_name)
            elif command == "team" and len(args) >= 1:
                description = " ".join(args)
                result = await self.team_module.suggest_team(description)
            else:
                error_msg = "Invalid command. Available commands: get info, compare, strategy, team"
                self.logger.log_error(ValueError(error_msg), "Invalid command")
                return {"error": error_msg}
            
            # Log successful response
            self.logger.log_server_activity(f"Successfully processed query: {query}")
            return {"response": result}
            
        except Exception as e:
            # Log the error
            self.logger.log_error(e, f"Error processing query: {query}")
            return {"error": str(e)}
    
    async def start(self):
        """Start the MCP server."""
        self.logger.log_server_activity("Starting Pokemon MCP Server...")
        
        while True:
            try:
                # Read request from stdin
                request_line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not request_line:
                    break
                
                # Clean the input
                request_line = request_line.strip()
                if not request_line:
                    continue
                
                try:
                    # Parse request
                    request = json.loads(request_line)
                except json.JSONDecodeError as e:
                    self.logger.log_error(e, f"Invalid JSON in request: {request_line}")
                    print(json.dumps({"error": "Invalid JSON format. Request must be a valid JSON object"}), flush=True)
                    continue
                
                # Process request
                response = await self.handle_request(request)
                
                # Send response
                print(json.dumps(response), flush=True)
                
            except Exception as e:
                self.logger.log_error(e, "Unexpected error in main loop")
                print(json.dumps({"error": "Internal server error"}), flush=True)
        
        self.logger.log_server_activity("Server shutting down...")

if __name__ == "__main__":
    server = PokemonMCPServer()
    asyncio.run(server.start())