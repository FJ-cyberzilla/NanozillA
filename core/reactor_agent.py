from google import genai
from google.genai.errors import APIError
from config.settings import settings
import streamlit as st
import time
from typing import Optional, Dict, Any
import traceback

# ============================================================================
# ASCII ART BANNERS
# ============================================================================
REACTOR_INIT = """
╔════════════════════════════════════════════════════════════════╗
║  🎮 REACTOR AGENT INITIALIZED                                 ║
╚════════════════════════════════════════════════════════════════╝
"""

PROCESSING_BANNER = """
╔════════════════════════════════════════════════════════════════╗
║  🔄🔄🔄  REACTOR PROCESSING  🔄🔄🔄                            ║
╚════════════════════════════════════════════════════════════════╝
"""

SUCCESS_BANNER = """
╔════════════════════════════════════════════════════════════════╗
║  ✅✅✅  COLORIZATION COMPLETE  ✅✅✅                          ║
╚════════════════════════════════════════════════════════════════╝
"""

ERROR_BANNER = """
╔════════════════════════════════════════════════════════════════╗
║  ⚠️⚠️⚠️  REACTOR AGENT ERROR  ⚠️⚠️⚠️                          ║
╚════════════════════════════════════════════════════════════════╝
"""


class ReactorAgent:
    """Enhanced Reactor Agent with 8-bit styling and comprehensive error handling"""

    def __init__(self):
        try:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.model = settings.MODEL_NAME
            self.generation_count = 0
            self.last_generation_time = None
            self.total_processing_time = 0

            # Rate limiting
            self.last_api_call_time = 0
            self.min_call_interval = 1.0

            self._validate_initialization()
            self._log_initialization()

        except Exception as e:
            self._handle_initialization_error(e)
            raise

    def _validate_initialization(self):
        """Validate initialization parameters"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        if not settings.MODEL_NAME:
            raise ValueError("MODEL_NAME not configured")

    def _log_initialization(self):
        """Log successful initialization with ASCII art"""
        init_msg = f"""
        <div class="status-box">
        ╔════════════════════════════════════════════════════════════════╗
        ║  🎮 REACTOR AGENT ONLINE                                      ║
        ╠════════════════════════════════════════════════════════════════╣
        ║  Model: {self.model[:40]:<40} ║
        ║  Status: READY FOR GENERATION                                ║
        ║  API: GOOGLE GEMINI                                          ║
        ╚════════════════════════════════════════════════════════════════╝
        </div>
        """
        st.markdown(init_msg, unsafe_allow_html=True)

    def _handle_initialization_error(self, error: Exception):
        """Handle initialization errors with ASCII styling"""
        error_msg = f"""
╔════════════════════════════════════════════════════════════════╗
║  ❌ REACTOR INITIALIZATION FAILED                             ║
╠════════════════════════════════════════════════════════════════╣
║  Error: {str(error)[:55]:<55} ║
╠════════════════════════════════════════════════════════════════╣
║  Please check:                                                ║
║  • GEMINI_API_KEY in .env file                               ║
║  • MODEL_NAME configuration                                  ║
║  • Internet connectivity                                     ║
╚════════════════════════════════════════════════════════════════╝
        """
        st.error(error_msg)

    def _enforce_rate_limit(self):
        """Enforce minimum time between API calls"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call_time

        if time_since_last_call < self.min_call_interval:
            sleep_time = self.min_call_interval - time_since_last_call
            time.sleep(sleep_time)

        self.last_api_call_time = time.time()

    def execute_colorization(
        self,
        image_bytes: bytes,
        style_prompt: str,
        quality: str = "high",
        safety_level: str = "block_some",
        retry_attempts: int = 3
    ) -> bytes:
        """
        Execute image colorization with enhanced error handling and ASCII UI

        Args:
            image_bytes: Input image as bytes
            style_prompt: Style description for transformation
            quality: Image quality ('low', 'medium', 'high')
            safety_level: Safety filter level
            retry_attempts: Number of retry attempts

        Returns:
            bytes: Generated image as bytes
        """

        # Validate inputs
        self._validate_inputs(image_bytes, style_prompt)

        # Show processing banner
        st.markdown(f"<pre>{PROCESSING_BANNER}</pre>", unsafe_allow_html=True)

        attempt = 0
        last_error = None

        while attempt < retry_attempts:
            try:
                attempt += 1

                # Log retry attempt
                if attempt > 1:
                    self._log_retry_attempt(attempt, retry_attempts)

                # Enforce rate limiting
                self._enforce_rate_limit()

                # Start timing
                start_time = time.time()

                # Prepare and execute API call
                result = self._call_gemini_api(
                    image_bytes=image_bytes,
                    style_prompt=style_prompt,
                    quality=quality,
                    safety_level=safety_level
                )

                # Process result
                image_data = self._process_api_result(result)

                # Calculate timing
                generation_time = time.time() - start_time
                self.last_generation_time = generation_time
                self.total_processing_time += generation_time
                self.generation_count += 1

                # Log success
                self._log_success(generation_time)

                return image_data

            except APIError as e:
                last_error = e
                self._handle_api_error(e, attempt, retry_attempts)

                if self._is_fatal_error(e):
                    break

                if attempt < retry_attempts:
                    self._wait_before_retry(attempt)

            except Exception as e:
                last_error = e
                self._handle_unexpected_error(e, attempt, retry_attempts)

                if attempt < retry_attempts:
                    self._wait_before_retry(attempt)

        # All retries exhausted
        self._handle_final_failure(last_error, retry_attempts)
        raise last_error

    def _validate_inputs(self, image_bytes: bytes, style_prompt: str):
        """Validate input parameters"""
        if not image_bytes or len(image_bytes) < 100:
            raise ValueError("Invalid image data: too small or empty")

        if not style_prompt or not style_prompt.strip():
            raise ValueError("Style prompt cannot be empty")

        if len(style_prompt) > settings.MAX_PROMPT_LENGTH:
            raise ValueError(
                f"Style prompt too long (max {settings.MAX_PROMPT_LENGTH} chars)"
            )

    def _call_gemini_api(self, image_bytes: bytes, style_prompt: str, quality: str, safety_level: str):
        """
        Make API call to Gemini
        """
        config = {
            "number_of_images": 1,
            "quality": quality,
            "safety_filter_level": safety_level
        }

        return self.client.models.generate_images(
            model=self.model,
            prompt=style_prompt,
            image=image_bytes,
            config=config
        )

    def _process_api_result(self, result) -> bytes:
        """
        Process and validate API result
        """
        if not result or not hasattr(result, 'generated_images'):
            raise ValueError("Invalid API response: missing generated_images")

        if not result.generated_images:
            raise ValueError("No images generated by API")

        try:
            image_data = result.generated_images[0].image.image_bytes

            if not image_data or len(image_data) < 100:
                raise ValueError("Generated image data is invalid or corrupted")

            return image_data

        except AttributeError as e:
            raise ValueError(f"Unable to extract image data: {str(e)}")

    def _is_fatal_error(self, error: APIError) -> bool:
        """
        Determine if error is fatal (no retry)
        """
        error_msg = str(error).lower()
        fatal_errors = [
            "invalid api key",
            "authentication failed",
            "permission denied",
            "model not found",
            "quota exceeded",
            "content policy violation"
        ]
        return any(fatal in error_msg for fatal in fatal_errors)

    def _wait_before_retry(self, attempt: int):
        """
        Wait before retry with exponential backoff
        """
        wait_time = 2 ** attempt
        st.warning(f"⏳ Waiting {wait_time}s before retry...")
        time.sleep(wait_time)

    def _log_retry_attempt(self, attempt: int, max_attempts: int):
        """
        Log retry attempt with ASCII art
        """
        retry_msg = f"""
        <div class="status-box">
        ╔════════════════════════════════════════════════════════════════╗
        ║  🔄 RETRY ATTEMPT {attempt}/{max_attempts}                                    ║
        ╚════════════════════════════════════════════════════════════════╝
        </div>
        """
        st.markdown(retry_msg, unsafe_allow_html=True)

    def _handle_api_error(self, error: APIError, attempt: int, max_attempts: int):
        """
        Handle API errors with detailed ASCII messages
        """
        error_msg = f"""
╔════════════════════════════════════════════════════════════════╗
║  ⚠️ GEMINI API ERROR (Attempt {attempt}/{max_attempts})                       ║
╠════════════════════════════════════════════════════════════════╣
║  Type: {type(error).__name__:<50} ║
║  Message: {str(error)[:50]:<50} ║
╚════════════════════════════════════════════════════════════════╝
        """
        st.error(error_msg)

    def _handle_unexpected_error(self, error: Exception, attempt: int, max_attempts: int):
        """
        Handle unexpected errors
        """
        error_msg = f"""
╔════════════════════════════════════════════════════════════════╗
║  ❌ UNEXPECTED ERROR (Attempt {attempt}/{max_attempts})                      ║
╠════════════════════════════════════════════════════════════════╣
║  Type: {type(error).__name__:<55} ║
║  Message: {str(error)[:53]:<53} ║
╚════════════════════════════════════════════════════════════════╝
        """
        st.error(error_msg)

        with st.expander("🔍 Technical Details"):
            st.code(traceback.format_exc())

    def _handle_final_failure(self, error: Exception, max_attempts: int):
        """
        Handle final failure after all retries
        """
        error_msg = f"""
╔════════════════════════════════════════════════════════════════╗
║  ❌❌❌ GENERATION FAILED AFTER {max_attempts} ATTEMPTS ❌❌❌             ║
╠════════════════════════════════════════════════════════════════╣
║  All retry attempts exhausted                                 ║
║  Last Error: {str(error)[:48]:<48} ║
╠════════════════════════════════════════════════════════════════╣
║  💡 TROUBLESHOOTING:                                          ║
║  • Check API key and quota                                   ║
║  • Simplify your style prompt                                ║
║  • Verify image format and size                              ║
║  • Check internet connection                                 ║
╚════════════════════════════════════════════════════════════════╝
        """
        st.error(error_msg)

    def _log_success(self, generation_time: float):
        """
        Log successful generation with ASCII art
        """
        success_msg = f"""
        <div class="status-box">
        ╔════════════════════════════════════════════════════════════════╗
        ║  ✅ GENERATION SUCCESSFUL                                     ║
        ╠════════════════════════════════════════════════════════════════╣
        ║  Time: {generation_time:.2f}s                                          ║
        ║  Total Generations: {self.generation_count:03d}                                ║
        ║  Avg Time: {self.total_processing_time/self.generation_count:.2f}s/generation     ║
        ╚════════════════════════════════════════════════════════════════╝
        </div>
        """
        st.markdown(success_msg, unsafe_allow_html=True)
        st.markdown(f"<pre>{SUCCESS_BANNER}</pre>", unsafe_allow_html=True)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive agent statistics
        """
        return {
            "generation_count": self.generation_count,
            "last_generation_time": self.last_generation_time,
            "total_processing_time": self.total_processing_time,
            "average_generation_time": self.total_processing_time / max(self.generation_count, 1),
            "model": self.model,
            "status": "operational"
        }


def create_reactor_agent() -> Optional[ReactorAgent]:
    """Create ReactorAgent with fallback error handling"""
    try:
        return ReactorAgent()
    except Exception as e:
        st.error(f"❌ Failed to create ReactorAgent: {str(e)}")
        return None
