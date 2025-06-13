# server.py
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from flask import Flask, jsonify, request
from enum import Enum
from outlines import models, generate
import uvicorn

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
mcp = FastMCP(name="demo")

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

# Generate a home from a home report
@mcp.tool()
def generate_home(home_report: str) -> Home:
    """Generate a filled home form with a home report, Given a long home report, extract relevant information and return a filled home form."""
    print("Generating home from report:", home_report)
    try:
        generator = ollama(Home)
        home = generator(home_report)
        print(home)
        return home.model_dump()
    except Exception as e:
        print("Error generating home:", e)
        return Message(success=False, message=str(e))
    
@mcp.tool()
def generate_appliance(appliance_report: str) -> list[Appliance]:
    """Extract a list of appliances from a home report. Given a long home report, extract relevant information about appliances and return a list of filled appliance forms."""
    print("Generating appliances from report:", appliance_report)
    try:
        generator = ollama(list[Appliance])
        appliances = generator(appliance_report)
        print(appliances)
        return appliances.model_dump()
    except Exception as e:
        print("Error generating appliances:", e)
        return Message(success=False, message=str(e))
    
@mcp.tool()
def generate_sensor(sensor_report: str) -> list[Sensor]:
    """Extract a list of sensors from a home report. Given a long home report, extract relevant information about sensors and return a list of filled sensor forms."""
    print("Generating sensors from report:", sensor_report)
    try:
        generator = ollama(list[Sensor])
        sensors = generator(sensor_report)
        print(sensors)
        return sensors.model_dump()
    except Exception as e:
        print("Error generating sensors:", e)
        return Message(success=False, message=str(e))        

if __name__ == "__main__":
    http_app = mcp.streamable_http_app()
    uvicorn.run(http_app, host="0.0.0.0", port=PORT, log_level="debug")