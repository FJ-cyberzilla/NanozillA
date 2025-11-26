from setuptools import setup, find_packages

setup(
    name="nanozilla-reactor",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.28.0",
        "google-genai==0.3.0", 
        "pillow==10.0.1",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "numpy==1.24.3",
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.5.0",
    ],
    python_requires=">=3.8",
)
