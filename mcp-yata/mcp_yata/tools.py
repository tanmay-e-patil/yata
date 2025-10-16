from typing import Dict, Any, List
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from .client import yata_client, TodoCreate, TodoUpdate


def setup_todo_tools(server: Server):
    """Setup todo-related tools"""
    
    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="create_todo",
                description="Create a new todo item",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the todo item"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the todo"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Whether the todo is completed (default: false)",
                            "default": False
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="list_todos",
                description="Get all todos for the authenticated user",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_todo",
                description="Get a specific todo by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "string",
                            "description": "ID of the todo to retrieve"
                        }
                    },
                    "required": ["todo_id"]
                }
            ),
            Tool(
                name="update_todo",
                description="Update an existing todo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "string",
                            "description": "ID of the todo to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the todo"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the todo"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Whether the todo is completed"
                        }
                    },
                    "required": ["todo_id"]
                }
            ),
            Tool(
                name="delete_todo",
                description="Delete a todo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "string",
                            "description": "ID of the todo to delete"
                        }
                    },
                    "required": ["todo_id"]
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls"""
        try:
            if name == "create_todo":
                todo = TodoCreate(
                    title=arguments["title"],
                    description=arguments.get("description"),
                    completed=arguments.get("completed", False)
                )
                result = await yata_client.create_todo(todo)
                return [TextContent(
                    type="text",
                    text=f"Todo created successfully:\nTitle: {result['title']}\nID: {result['id']}"
                )]
            
            elif name == "list_todos":
                todos = await yata_client.list_todos()
                if not todos:
                    return [TextContent(type="text", text="No todos found")]
                
                todo_list = "\n".join([
                    f"- {todo['title']} (ID: {todo['id']}, Completed: {todo['completed']})"
                    for todo in todos
                ])
                return [TextContent(type="text", text=f"Your todos:\n{todo_list}")]
            
            elif name == "get_todo":
                todo = await yata_client.get_todo(arguments["todo_id"])
                return [TextContent(
                    type="text",
                    text=f"Todo Details:\nTitle: {todo['title']}\nDescription: {todo.get('description', 'N/A')}\nCompleted: {todo['completed']}\nID: {todo['id']}"
                )]
            
            elif name == "update_todo":
                todo_id = arguments["todo_id"]
                update_data = TodoUpdate(**{k: v for k, v in arguments.items() if k != "todo_id" and v is not None})
                result = await yata_client.update_todo(todo_id, update_data)
                return [TextContent(
                    type="text",
                    text=f"Todo updated successfully:\nTitle: {result['title']}\nID: {result['id']}"
                )]
            
            elif name == "delete_todo":
                result = await yata_client.delete_todo(arguments["todo_id"])
                return [TextContent(type="text", text=result["message"])]
            
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]