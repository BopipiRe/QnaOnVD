import json
import sqlite3

import jsonschema

from settings import schema


class ToolDB:
    def __init__(self, db_path="resources/tools.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS http_tools (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            type TEXT NOT NULL,
            config TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    def save_tool(self, config):
        jsonschema.validate(instance=config, schema=schema)
        self.conn.execute(
            "INSERT OR REPLACE INTO http_tools (name, type, config) VALUES (?, ?, ?)",
            (config["name"], config["type"], json.dumps(config))
        )
        self.conn.commit()

    def delete_tool(self, name):
        self.conn.execute("DELETE FROM http_tools WHERE name = ?", (name,))
        self.conn.commit()

    def load_all_tools(self):
        cursor = self.conn.execute("SELECT config FROM http_tools")
        return [json.loads(row[0]) for row in cursor]

    def load_tools_by_type(self, tool_type):
        cursor = self.conn.execute("SELECT config FROM http_tools WHERE type = ?", (tool_type,))
        return [json.loads(row[0]) for row in cursor]


if __name__ == "__main__":
    db = ToolDB(db_path="../resources/tools.db")
    config = {
        "name": "chat",
        "description": "chat",
        "method": "GET",
        "type": "API",
        "url": "http://127.0.0.1:5000/chat",
        "input_schema": {
            "query": {"type": "string", "required": True},
        }
    }
    test_config = {
        "name": "test",
        "description": "test",
        "method": "GET",
        "type": "API",
        "url": "http://127.0.0.1:5000/test",
        "input_schema": {
            "input1": {"type": "int", "required": True},
            "input2": {"type": "string", "required": True}
        }
    }
    db.save_tool(config)
    db.save_tool(test_config)
    print(db.load_all_tools())
