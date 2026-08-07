import os
from fastapi import FastAPI
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


load_dotenv()



