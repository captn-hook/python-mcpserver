# server.py
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from flask import Flask, jsonify, request
from enum import Enum
from openai import AsyncOpenAI
from outlines import models, generate
from outlines.models.openai import OpenAIConfig
import uvicorn
import asyncio

# Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
PORT = int(os.getenv("PORT", 8000))

def fill_form(info: str) -> str:
    return "You are a property manager. Customers \
    send you inspection reports from which you need to extract \
    the relevant information to fill out the home form. \
    Here is the inspection report: {info} \
    Fill out the home form as completely as possible."
    



def fill_home_form(form: str) -> str:
    return f"You are a property manager. Customers \
    send you inspection reports from which you need to extract \
    the relevant information to fill out the home form. \
    Home forms have information about the home, such as address, \
    type (e.g., apartment, detached, semi-detached, terraced), \
    year built, square footage, number of floors, number of bathrooms, etc. \
    Leave any unspecified fields empty. Here is the inspection report: {form} \
    Fill out the home form as completely as possible."

def fill_appliance_form(form: str) -> str:
    return f"You are a property manager. Customers \
    send you inspection reports from which you need to extract \
    the relevant information to fill out the appliance form. \
    Appliance forms have information about appliances in the home, \
    such as name, serial number, warranty, age, room, and installation date. \
    Leave any unspecified fields empty. Here is the inspection report: {form} \
    Fill out the appliance form as completely as possible."

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
            base_url="http://localhost:11434/v1",
            api_key='ollama'
        )
    except Exception as e:
        print("Error loading model")
        raise e

    async def generate_async(prompt):
        return await generate.json(model, Class, prompt)

    def generate_sync(prompt):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Use asyncio.run_coroutine_threadsafe if already in an event loop
            future = asyncio.run_coroutine_threadsafe(generate_async(prompt), loop)
            return future.result()
        else:
            return asyncio.run(generate_async(prompt))

    return generate_sync
# Generate a home from a home report
@mcp.tool()
def generate_home(home_report: str) -> Home:
    """Generate a filled home form with a home report, Given an entire home report, extract relevant information and return a filled home form."""
    print("Generating home from report:", home_report)
    try:
        generator = ollama(Home)
        home = generator(fill_home_form(home_report))
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
        appliances = generator(fill_appliance_form(appliance_report))
        print(appliances)
        return appliances.model_dump()
    except Exception as e:
        print("Error generating appliances:", e)
        return Message(success=False, message=str(e))
    
@mcp.tool()
def generate_sensor(sensor_report: str) -> list[Sensor]:
    """Extract a list of sensors from a home report. Given a long home report, extract relevant information about sensors and return a list of filled sensor forms."""
    print("Generating sensors from report:", sensor_report)
    return Message(success=False, message="This tool is not implemented yet. Please try again later.")
    
    try:
        generator = ollama(list[Sensor])
        sensors = generator(fill_sensor_form(sensor_report))
        print(sensors)
        return sensors.model_dump()
    except Exception as e:
        print("Error generating sensors:", e)
        return Message(success=False, message=str(e))        

if __name__ == "__main__":
    http_app = mcp.streamable_http_app()
    uvicorn.run(http_app, host="0.0.0.0", port=PORT, log_level="debug")