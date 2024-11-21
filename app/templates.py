from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

# Create a Jinja2 environment with auto-reload enabled
jinja_env = Environment(loader=FileSystemLoader("app/templates"), auto_reload=True)

# Use the custom environment in Jinja2Templates
templates = Jinja2Templates(env=jinja_env)
