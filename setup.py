from setuptools import setup, find_packages

setup(
    name="nanozilla-reactor",
    version="2.0.0",
    author="NanozillA",
    author_email="<your-email>",
    description="A Python-based application that provides a core API server, image processing capabilities, and a reactor agent.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/NanozillA",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.37.0",
        "google-genai==0.3.0",
        "pillow==10.3.0",
        "python-dotenv==1.0.0",
        "requests==2.32.4",
        "numpy==1.24.3",
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.5.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.8",
)
