# server.py
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from flask import Flask, jsonify, request
from enum import Enum
from outlines import models, generate

# Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
PORT = int(os.getenv("PORT", 8000))

class Appliance(BaseModel):
    name: str = Field(
        default="",
        description="The name of the appliance.",
    )
    serial_number: str = Field(
        default="",
        description="The serial number of the appliance.",
    )
    warranty: str = Field(
        default="",
        description="The warranty information of the appliance.",
    )
    age: int = Field(
        default=0,
        description="The age of the appliance in years.",
    )
    room: str = Field(
        default="",
        description="The room where the appliance is located.",
    )
    installation_date: str = Field(
        default="",
        description="The installation date of the appliance.",
    )

class Sensor(BaseModel):
    name: str = Field(
        default="",
        description="The name of the sensor.",
    )
    type: str = Field(
        default="",
        description="The type of sensor (e.g., temperature, humidity, smoke).",
    )
    location: str = Field(
        default="",
        description="The location of the sensor in the home.",
    )

class Home(BaseModel):
    home_address: str = Field(
        default="",
        description="The home address of the patient.",
    )
    home_type: str = Field(
        default="",
        description="The type of home (e.g., apartment, detached, semi-detached, terraced).",
    )
    year_built: int = Field(
        default=0,
        description="The year the home was built.",
    )
    location: str = Field(
        default="",
        description="The location of the home (latitude and longitude).",
    )
    square_footage: int = Field(
        default=0,
        description="The square footage of the home.",
    )
    number_of_floors: int = Field(
        default=0,
        description="The number of floors in the home.",
    )
    number_of_living_rooms: int = Field(
        default=0,
        description="The number of living rooms in the home.",
    )
    number_of_bedrooms: int = Field(
        default=0,
        description="The number of bedrooms in the home.",
    )
    number_of_bathrooms: int = Field(
        default=0,
        description="The number of bathrooms in the home.",
    )
    basement: bool = Field(
        default=False,
        description="Whether the home has a basement.",
    )
    garage: bool = Field(
        default=False,
        description="Whether the home has a garage.",
    )
    wall_type: str = Field(
        default="",
        description="The type of walls in the home (e.g., brick, wood, concrete).",
    )
    pool: bool = Field(
        default=False,
        description="Whether the home has a pool.",
    )
    septic_tank: bool = Field(
        default=False,
        description="Whether the home has a septic tank.",
    )
    roof_type: str = Field(
        default="",
        description="The type of roof (e.g., flat, pitched, gabled).",
    )
    weather_conditions: str = Field(
        default="", # try to fetch this from the weather API
        description="The weather conditions in the area (e.g., humid, dry, rainy).",
    )

class Message(BaseModel):
    success: bool = Field(
        default=False,
        description="Whether the message indicates failure or success.",
    )
    message: str = Field(
        default="",
        description="The message content.",
    )
# Create an MCP server
mcp = FastMCP(name="demo", json_response=False, stateless_http=False)

def ollama(Class):
    try:
        model = models.openai(
            "gemma3:4b",
            base_url=OLLAMA_URL + "/v1",
            api_key='ollama'
        )
    except Exception as e:
        print("Error loading model:", e)

    return generate.json(model, Class)

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Generate a home from a home report
@mcp.resource("home://{home_report}")
def generate_home(home_report: str) -> Home:
    """Generate a home from a home report"""
    try:
        generator = ollama(Home)
        home = generator.generate(home_report)
        return home.model_dump()
    except Exception as e:
        print("Error generating home:", e)
        return Message(success=False, message=str(e))
    
@mcp.resource("appliances://{appliance_report}")
def generate_appliance(appliance_report: str) -> list[Appliance]:
    """Generate an appliance from a report"""
    try:
        generator = ollama(list[Appliance])
        appliances = generator.generate(appliance_report)
        return appliances.model_dump()
    except Exception as e:
        print("Error generating appliances:", e)
        return Message(success=False, message=str(e))
    
@mcp.resource("sensors://{sensor_report}")
def generate_sensor(sensor_report: str) -> list[Sensor]:
    """Generate a sensor from a report"""
    try:
        generator = ollama(list[Sensor])
        sensors = generator.generate(sensor_report)
        return sensors.model_dump()
    except Exception as e:
        print("Error generating sensors:", e)
        return Message(success=False, message=str(e))        
        
        
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http"
    )