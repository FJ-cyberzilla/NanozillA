from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio

from core.reactor_agent import create_reactor_agent
from core.image_processor import create_image_processor
from utils.validators import validate_prompt
from utils.spell_checker import check_style_prompt

# ============================================================================
# API MODELS
# ============================================================================


class ColorizationRequest(BaseModel):
    style_prompt: str = Field(..., min_length=10, max_length=2000)
    quality: str = Field("high", regex="^(high|medium|low)$")
    safety_level: str = Field("block_some", regex="^(block_some|block_most|block_none)$")
    output_format: str = Field("png", regex="^(png|jpeg|webp)$")


class BatchColorizationRequest(BaseModel):
    style_prompt: str = Field(..., min_length=10, max_length=2000)
    concurrent: int = Field(3, ge=1, le=5)


class ColorizationResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# ============================================================================
# API SERVER
# ============================================================================


class NANozILLAAPI:
    """
    FastAPI server for NANozILLA Reactor API
    """

    def __init__(self):
        self.app = FastAPI(
            title="NANozILLA Reactor API",
            description="Vintage 8-bit AI Image Colorization API",
            version="2.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc"
        )

        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # State
        self.reactor_agent = None
        self.image_processor = None
        self.jobs = {}  # In-memory job storage

        # Setup routes
        self._setup_routes()
        self._setup_exception_handlers()

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/")
        async def root():
            return {
                "message": "🎮 NANozILLA Reactor API v2.0",
                "status": "operational",
                "version": "2.0.0"
            }

        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "reactor_agent": "operational" if self.reactor_agent else "offline",
                    "image_processor": "operational" if self.image_processor else "offline"
                }
            }

        @self.app.post("/api/v1/colorize", response_model=ColorizationResponse)
        async def colorize_image(
            background_tasks: BackgroundTasks,
            image: UploadFile = File(..., description="Image file to colorize"),
            style_prompt: str = Form(..., description="Style description"),
            quality: str = Form("high"),
            safety_level: str = Form("block_some"),
            output_format: str = Form("png")
        ):
            """
            Colorize a single image with AI
            """
            try:
                # Validate inputs
                if not image.content_type.startswith('image/'):
                    raise HTTPException(400, "File must be an image")

                validate_prompt(style_prompt)

                # Spell check prompt
                corrected_prompt, _ = check_style_prompt(style_prompt)

                # Initialize components if needed
                if not self.reactor_agent:
                    self.reactor_agent = create_reactor_agent()
                if not self.image_processor:
                    self.image_processor = create_image_processor()

                if not self.reactor_agent or not self.image_processor:
                    raise HTTPException(503, "Service components not available")

                # Process image
                image_data = await image.read()

                # Create in-memory file-like object
                class UploadFileWrapper:
                    def __init__(self, data, filename, content_type):
                        self.data = data
                        self.name = filename
                        self.type = content_type

                    def getvalue(self):
                        return self.data

                wrapped_file = UploadFileWrapper(image_data, image.filename, image.content_type)

                # Process image
                processed_bytes, image_info = self.image_processor.process_uploaded_image(
                    wrapped_file, validate_colors=True, auto_resize=True
                )

                # Generate colorization
                generated_bytes = self.reactor_agent.execute_colorization(
                    image_bytes=processed_bytes,
                    style_prompt=corrected_prompt,
                    quality=quality,
                    safety_level=safety_level,
                    retry_attempts=3
                )

                # Convert format if needed
                if output_format.lower() != 'png':
                    converted_bytes, _ = self.image_processor.convert_format(
                        generated_bytes, output_format.upper()
                    )
                    generated_bytes = converted_bytes

                # Prepare response
                response_data = {
                    "image_data": generated_bytes.hex(),  # Convert to hex for JSON
                    "generation_id": f"gen_{uuid.uuid4().hex[:12]}",
                    "processing_time": self.reactor_agent.last_generation_time,
                    "image_info": {
                        "format": output_format.upper(),
                        "width": image_info.get('width'),
                        "height": image_info.get('height'),
                        "file_size": len(generated_bytes),
                        "color_mode": image_info.get('color_analysis', {}).get('color_mode', 'RGB')
                    },
                    "style_prompt_used": corrected_prompt
                }

                return ColorizationResponse(
                    success=True,
                    data=response_data,
                    metadata={
                        "version": "2.0.0",
                        "model": self.reactor_agent.model,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

            except ValueError as e:
                raise HTTPException(400, f"Validation error: {str(e)}")
            except Exception as e:
                raise HTTPException(500, f"Processing error: {str(e)}")

        @self.app.post("/api/v1/colorize/batch")
        async def batch_colorize(
            background_tasks: BackgroundTasks,
            images: List[UploadFile] = File(..., description="Multiple image files"),
            style_prompt: str = Form(..., description="Style description for all images"),
            concurrent: int = Form(3)
        ):
            """
            Process multiple images in batch
            """
            try:
                # Validate inputs
                if len(images) > 10:
                    raise HTTPException(400, "Maximum 10 images per batch")

                validate_prompt(style_prompt)

                # Create job
                job_id = f"batch_{uuid.uuid4().hex[:12]}"
                job = {
                    "job_id": job_id,
                    "status": "processing",
                    "progress": 0,
                    "total_images": len(images),
                    "processed_images": 0,
                    "results": [],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                self.jobs[job_id] = job

                # Process in background
                background_tasks.add_task(
                    self._process_batch_job, job_id, images, style_prompt, concurrent
                )

                return {
                    "success": True,
                    "data": {
                        "job_id": job_id,
                        "status": "processing",
                        "total_images": len(images)
                    },
                    "metadata": {
                        "version": "2.0.0",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }

            except Exception as e:
                raise HTTPException(500, f"Batch processing error: {str(e)}")

        @self.app.get("/api/v1/jobs/{job_id}")
        async def get_job_status(job_id: str):
            """
            Get status of a batch processing job
            """
            job = self.jobs.get(job_id)
            if not job:
                raise HTTPException(404, "Job not found")

            return {
                "success": True,
                "data": job,
                "metadata": {
                    "version": "2.0.0",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        @self.app.get("/api/v1/analytics/usage")
        async def get_usage_analytics():
            """
            Get usage statistics and analytics
            """
            if not self.reactor_agent:
                stats = {}
            else:
                stats = self.reactor_agent.get_stats()

            return {
                "success": True,
                "data": {
                    "plan": "pro",
                    "monthly_quota": 1000,
                    "requests_used": stats.get('generation_count', 0),
                    "requests_remaining": (
                        1000 - stats.get('generation_count', 0)
                    ),
                    "reset_date": "2024-02-01T00:00:00Z",
                    "metrics": {
                        "total_generations": stats.get('generation_count', 0),
                        "success_rate": 0.94,
                        "average_processing_time": stats.get(
                            'average_generation_time', 0
                        ),
                        "total_processing_time": stats.get(
                            'total_processing_time', 0
                        )
                    }
                },
                "metadata": {
                    "version": "2.0.0",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    def _setup_exception_handlers(self):
        """Setup global exception handlers"""

        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request, exc):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": exc.status_code,
                        "message": exc.detail
                    },
                    "metadata": {
                        "version": "2.0.0",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )

        @self.app.exception_handler(Exception)
        async def general_exception_handler(request, exc):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An internal server error occurred"
                    },
                    "metadata": {
                        "version": "2.0.0",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )

    async def _process_batch_job(self, job_id: str, images: List[UploadFile], style_prompt: str, concurrent: int):
        """Process batch job in background"""
        try:
            job = self.jobs[job_id]
            results = []

            # Initialize components
            if not self.reactor_agent:
                self.reactor_agent = create_reactor_agent()
            if not self.image_processor:
                self.image_processor = create_image_processor()

            # Process images with concurrency limit
            semaphore = asyncio.Semaphore(concurrent)

            async def process_single_image(image_file, index):
                async with semaphore:
                    try:
                        # Read and process image
                        image_data = await image_file.read()

                        class UploadFileWrapper:
                            def __init__(self, data, filename):
                                self.data = data
                                self.name = filename
                                self.type = 'image/jpeg'

                            def getvalue(self):
                                return self.data

                        wrapped_file = UploadFileWrapper(image_data, image_file.filename)

                        # Process image
                        processed_bytes, image_info = self.image_processor.process_uploaded_image(
                            wrapped_file)

                        # Generate colorization
                        generated_bytes = self.reactor_agent.execute_colorization(
                            image_bytes=processed_bytes,
                            style_prompt=style_prompt,
                            quality="high",
                            safety_level="block_some"
                        )

                        result = {
                            "original_filename": image_file.filename,
                            "success": True,
                            "image_data": generated_bytes.hex(),
                            "processing_time": self.reactor_agent.last_generation_time,
                            "image_info": image_info
                        }

                    except Exception as e:
                        result = {
                            "original_filename": image_file.filename,
                            "success": False,
                            "error": str(e),
                            "processing_time": 0
                        }

                    return result

            # Process all images
            tasks = [process_single_image(img, i) for i, img in enumerate(images)]
            batch_results = await asyncio.gather(*tasks)

            # Update job
            job["status"] = "completed"
            job["progress"] = 100
            job["processed_images"] = len(images)
            job["results"] = batch_results
            job["updated_at"] = datetime.utcnow()

        except Exception as e:
            job["status"] = "failed"
            job["error_message"] = str(e)
            job["updated_at"] = datetime.utcnow()


# Create API server instance
api_server = NANozILLAAPI()
app = api_server.app

# Run with: uvicorn core.api_server:app --host 0.0.0.0 --port 8000
