"""
Code generation tools for the skills pattern.

Provides boilerplate generation for common project types.
"""

from langchain_core.tools import tool


@tool
def generate_boilerplate(project_type: str, name: str) -> str:
    """Generate boilerplate code for common project types.

    Args:
        project_type: Type of project (python_cli, python_api, react_app, go_api)
        name: Name for the project/module
    """
    boilerplates = {
        "python_cli": f'''#!/usr/bin/env python3
"""
{name} - CLI Application
"""

import argparse
import logging
import sys
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> int:
    """Main entry point."""
    logger.info(f"Starting {name}")
    # Your logic here
    return 0


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="{name} - Description here",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    sys.exit(main(args))
''',

        "python_api": f'''"""
{name} - FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(
    title="{name}",
    description="API description here",
    version="0.1.0"
)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


@app.get("/")
async def root():
    """Health check endpoint."""
    return {{"status": "healthy", "service": "{name}"}}


@app.get("/items/{{item_id}}")
async def get_item(item_id: int):
    """Get item by ID."""
    return {{"item_id": item_id, "name": "Sample Item"}}


@app.post("/items")
async def create_item(item: Item):
    """Create a new item."""
    return {{"message": "Item created", "item": item}}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',

        "react_app": f'''// {name} - React Component
import React, {{ useState, useCallback }} from 'react';

interface {name}Props {{
  title: string;
  onSubmit?: (data: FormData) => void;
}}

interface FormData {{
  name: string;
  email: string;
}}

export const {name}: React.FC<{name}Props> = ({{ title, onSubmit }}) => {{
  const [formData, setFormData] = useState<FormData>({{
    name: '',
    email: ''
  }});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {{
    const {{ name, value }} = e.target;
    setFormData(prev => ({{ ...prev, [name]: value }}));
  }}, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {{
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {{
      onSubmit?.(formData);
    }} catch (err) {{
      setError(err instanceof Error ? err.message : 'An error occurred');
    }} finally {{
      setIsLoading(false);
    }}
  }}, [formData, onSubmit]);

  return (
    <div className="{name.lower()}-container">
      <h1>{{title}}</h1>
      {{error && <div className="error">{{error}}</div>}}
      <form onSubmit={{handleSubmit}}>
        <input name="name" value={{formData.name}} onChange={{handleChange}} placeholder="Name" />
        <input name="email" type="email" value={{formData.email}} onChange={{handleChange}} placeholder="Email" />
        <button type="submit" disabled={{isLoading}}>
          {{isLoading ? 'Loading...' : 'Submit'}}
        </button>
      </form>
    </div>
  );
}};

export default {name};
''',

        "go_api": f'''// {name} - Go HTTP API
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "os"
    "os/signal"
    "context"
    "syscall"
    "time"
)

type Item struct {{
    ID          int     `json:"id"`
    Name        string  `json:"name"`
    Description string  `json:"description,omitempty"`
    Price       float64 `json:"price"`
}}

type Response struct {{
    Status  string      `json:"status"`
    Data    interface{{}} `json:"data,omitempty"`
    Message string      `json:"message,omitempty"`
}}

func main() {{
    mux := http.NewServeMux()

    mux.HandleFunc("GET /", healthHandler)
    mux.HandleFunc("GET /items/{{id}}", getItemHandler)
    mux.HandleFunc("POST /items", createItemHandler)

    server := &http.Server{{
        Addr:         ":8080",
        Handler:      mux,
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
    }}

    // Graceful shutdown
    go func() {{
        sigChan := make(chan os.Signal, 1)
        signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
        <-sigChan

        ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()

        log.Println("Shutting down server...")
        server.Shutdown(ctx)
    }}()

    log.Printf("{name} starting on %s", server.Addr)
    if err := server.ListenAndServe(); err != http.ErrServerClosed {{
        log.Fatal(err)
    }}
}}

func healthHandler(w http.ResponseWriter, r *http.Request) {{
    json.NewEncoder(w).Encode(Response{{
        Status:  "healthy",
        Message: "{name} is running",
    }})
}}

func getItemHandler(w http.ResponseWriter, r *http.Request) {{
    id := r.PathValue("id")
    item := Item{{ID: 1, Name: "Sample", Price: 9.99}}
    json.NewEncoder(w).Encode(Response{{
        Status: "success",
        Data:   item,
    }})
    _ = id // use id to fetch from DB
}}

func createItemHandler(w http.ResponseWriter, r *http.Request) {{
    var item Item
    if err := json.NewDecoder(r.Body).Decode(&item); err != nil {{
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }}
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(Response{{
        Status:  "created",
        Data:    item,
    }})
}}
'''
    }

    project_type = project_type.lower().replace(" ", "_")
    if project_type not in boilerplates:
        return f"Unknown project type. Available: {', '.join(boilerplates.keys())}"

    return f"Generated boilerplate for {project_type}:\n\n```\n{boilerplates[project_type]}\n```"
