import streamlit as st
from core.reactor_agent import create_reactor_agent
from core.image_processor import create_image_processor
from utils.validators import validate_prompt
import io
import time
import traceback
# Add to imports
from utils.spell_checker import check_style_prompt, display_spelling_help, spell_checker

# ============================================================================
# ASCII ART BANNER - NANOZILLA
# ============================================================================
ASCII_BANNER = """
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║  ███╗   ██╗ █████╗ ███╗   ██╗ ██████╗ ███████╗██╗██╗     ██╗      █████╗  ║
║  ████╗  ██║██╔══██╗████╗  ██║██╔═══██╗╚══███╔╝██║██║     ██║     ██╔══██╗ ║
║  ██╔██╗ ██║███████║██╔██╗ ██║██║   ██║  ███╔╝ ██║██║     ██║     ███████║ ║
║  ██║╚██╗██║██╔══██║██║╚██╗██║██║   ██║ ███╔╝  ██║██║     ██║     ██╔══██║ ║
║  ██║ ╚████║██║  ██║██║ ╚████║╚██████╔╝███████╗██║███████╗███████╗██║  ██║ ║
║  ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚══════╝╚═╝  ╚═╝ ║
║                                                                          ║
║         ▓▓▓▓▓  AI-POWERED IMAGE COLORIZER v2.0  ▓▓▓▓▓                   ║
║              ░░░  VINTAGE 8-BIT EDITION  ░░░                            ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

MENU_TOP = """
╔════════════════════════════════════════════════════════════════╗
"""

MENU_BOTTOM = """
╚════════════════════════════════════════════════════════════════╝
"""

PIXEL_DIVIDER = "▓▒░" * 25

# ============================================================================
# CUSTOM CSS FOR VINTAGE 8-BIT AESTHETIC
# ============================================================================
VINTAGE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #00ff41;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #16213e 100%);
        border-right: 3px solid #00ff41;
    }
    
    /* Headers with 8-bit style */
    h1, h2, h3 {
        font-family: 'Press Start 2P', cursive !important;
        color: #00ff41;
        text-shadow: 3px 3px 0px #ff006e, 6px 6px 0px #8338ec;
        letter-spacing: 2px;
    }
    
    /* ASCII pre text */
    pre {
        font-family: 'Courier New', monospace;
        color: #00ff41;
        background: #000000;
        padding: 20px;
        border: 3px solid #00ff41;
        border-radius: 0px;
        box-shadow: 0 0 20px #00ff41;
        line-height: 1.2;
    }
    
    /* Buttons with retro style */
    .stButton > button {
        font-family: 'Press Start 2P', cursive;
        background: linear-gradient(135deg, #ff006e 0%, #8338ec 100%);
        color: #ffffff;
        border: 3px solid #00ff41;
        border-radius: 0px;
        padding: 15px 30px;
        font-size: 12px;
        text-transform: uppercase;
        box-shadow: 5px 5px 0px #00ff41;
        transition: all 0.1s;
    }
    
    .stButton > button:hover {
        transform: translate(2px, 2px);
        box-shadow: 3px 3px 0px #00ff41;
        background: linear-gradient(135deg, #8338ec 0%, #ff006e 100%);
    }
    
    .stButton > button:active {
        transform: translate(5px, 5px);
        box-shadow: 0px 0px 0px #00ff41;
    }
    
    /* Text input and text area */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-family: 'Courier New', monospace;
        background: #000000;
        color: #00ff41;
        border: 2px solid #00ff41;
        border-radius: 0px;
        font-size: 14px;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #0a0e27;
        border: 3px dashed #00ff41;
        border-radius: 0px;
        padding: 20px;
    }
    
    /* Success/Error/Info messages */
    .stSuccess {
        background: #000000;
        border: 3px solid #00ff41;
        border-radius: 0px;
        color: #00ff41;
        font-family: 'Courier New', monospace;
        padding: 15px;
    }
    
    .stError {
        background: #000000;
        border: 3px solid #ff006e;
        border-radius: 0px;
        color: #ff006e;
        font-family: 'Courier New', monospace;
        padding: 15px;
    }
    
    .stInfo {
        background: #000000;
        border: 3px solid #8338ec;
        border-radius: 0px;
        color: #8338ec;
        font-family: 'Courier New', monospace;
        padding: 15px;
    }
    
    .stWarning {
        background: #000000;
        border: 3px solid #ffbe0b;
        border-radius: 0px;
        color: #ffbe0b;
        font-family: 'Courier New', monospace;
        padding: 15px;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00ff41 0%, #8338ec 50%, #ff006e 100%);
    }
    
    /* Download button */
    .stDownloadButton > button {
        font-family: 'Press Start 2P', cursive;
        background: #8338ec;
        color: #ffffff;
        border: 3px solid #00ff41;
        border-radius: 0px;
        font-size: 10px;
        box-shadow: 3px 3px 0px #00ff41;
    }
    
    /* Image containers */
    [data-testid="stImage"] {
        border: 5px solid #00ff41;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.5);
        image-rendering: pixelated;
    }
    
    /* Columns */
    [data-testid="column"] {
        background: rgba(10, 14, 39, 0.5);
        border: 2px solid #00ff41;
        padding: 15px;
        margin: 5px;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #00ff41 !important;
        border-right-color: #ff006e !important;
        border-bottom-color: #8338ec !important;
        border-left-color: #ffbe0b !important;
    }
    
    /* Custom status box */
    .status-box {
        background: #000000;
        border: 3px solid #00ff41;
        padding: 15px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        color: #00ff41;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
    }
    
    /* Pixel art divider */
    .pixel-divider {
        color: #8338ec;
        font-size: 8px;
        text-align: center;
        margin: 20px 0;
    }
</style>
"""

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================


class SessionStateManager:
    """Manage session state variables"""

    @staticmethod
    def initialize():
        """Initialize all session state variables"""
        defaults = {
            'generated_image': None,
            'processing': False,
            'error_count': 0,
            'success_count': 0,
            'last_error': None,
            'generation_time': None,
            'uploaded_file_name': None,
            'reactor_agent': None,
            'image_processor': None
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def reset():
        """Reset session state"""
        st.session_state.generated_image = None
        st.session_state.processing = False
        st.session_state.generation_time = None
        st.session_state.uploaded_file_name = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def display_ascii_banner():
    """Display the ASCII art banner"""
    st.markdown(f"<pre>{ASCII_BANNER}</pre>", unsafe_allow_html=True)


def display_stats_panel():
    """Display statistics panel"""
    stats_html = f"""
    <div class="status-box">
    ╔════════════════════════════════════════════════════════════════╗
    ║  📊 SESSION STATISTICS                                        ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  ✅ Successful Generations: {st.session_state.success_count:03d}                     ║
    ║  ❌ Failed Attempts: {st.session_state.error_count:03d}                              ║
    ║  ⏱️  Last Generation Time: {st.session_state.generation_time or 'N/A':>20} ║
    ╚════════════════════════════════════════════════════════════════╝
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)


def display_pixel_divider():
    """Display pixel art divider"""
    st.markdown(f'<div class="pixel-divider">{PIXEL_DIVIDER}</div>', unsafe_allow_html=True)


def initialize_components():
    """Initialize Reactor Agent and Image Processor"""
    if st.session_state.reactor_agent is None:
        st.session_state.reactor_agent = create_reactor_agent()

    if st.session_state.image_processor is None:
        st.session_state.image_processor = create_image_processor()


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="NanozillA - 8-Bit Image Colorizer",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(VINTAGE_CSS, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================


def main():
    """Main application logic"""

    # Initialize session state
    SessionStateManager.initialize()
    initialize_components()

    # Display banner
    display_ascii_banner()

    # Display stats
    display_stats_panel()
    display_pixel_divider()

    # ========================================================================
    # SIDEBAR CONFIGURATION
    # ========================================================================
    with st.sidebar:
        st.markdown(f"<pre>{MENU_TOP}</pre>", unsafe_allow_html=True)
        st.markdown("### ⚙️ CONFIGURATION PANEL")
        st.markdown(f"<pre>{MENU_BOTTOM}</pre>", unsafe_allow_html=True)

        # File upload section
        st.markdown("#### 📁 FILE UPLOAD")
        uploaded_file = st.file_uploader(
            "Select Image File",
            type=['jpg', 'jpeg', 'png', 'webp'],
            help="Upload a black & white or color image to transform",
            label_visibility="collapsed"
        )

        if uploaded_file:
            try:
                st.success(f"✓ {uploaded_file.name}")
                st.session_state.uploaded_file_name = uploaded_file.name
            except Exception as e:
                st.error(f"✗ {str(e)}")
                uploaded_file = None

        st.markdown("---")

        # Style prompt section
        st.markdown("#### 🎨 STYLE PROMPT")
        style_prompt = st.text_area(
            "Transformation Style",
            placeholder="Enter your creative vision...\n\nExamples:\n• Vibrant anime style\n• Vintage 1950s colors\n• Cyberpunk neon aesthetic\n• Watercolor painting effect",
            height=150,
            label_visibility="collapsed"
        )

        # SPELL CHECKING - MOVED INSIDE SIDEBAR
        if style_prompt:
            char_count = len(style_prompt)
            st.caption(f"Characters: {char_count}/2000")

            # Auto spell check
            corrected_prompt, spelling_issues = check_style_prompt(style_prompt)
            if corrected_prompt != style_prompt:
                style_prompt = corrected_prompt
                # Update the text area
                st.session_state.auto_corrected_prompt = corrected_prompt

            # Display spelling issues
            if spelling_issues:
                spell_checker.display_spelling_issues(spelling_issues)

        st.markdown("---")

        # Advanced settings
        with st.expander("⚡ ADVANCED SETTINGS"):
            quality = st.selectbox(
                "Image Quality",
                ["high", "medium", "low"],
                index=0,
                help="Higher quality = longer processing time"
            )

            safety_level = st.selectbox(
                "Safety Filter",
                ["block_some", "block_most", "block_none"],
                index=0,
                help="Content safety filtering level"
            )

            retry_attempts = st.slider(
                "Retry Attempts",
                min_value=1,
                max_value=5,
                value=3,
                help="Number of retry attempts on failure"
            )

        st.markdown("---")

        # Generate button
        generate_btn = st.button(
            "🚀 GENERATE TRANSFORMATION",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.processing
        )

        # Reset button
        if st.button("🔄 RESET SESSION", use_container_width=True):
            SessionStateManager.reset()
            st.rerun()

        st.markdown("---")

        # Help section with spell checking help
        with st.expander("ℹ️ HELP & TIPS"):
            st.markdown("""
            **How to use NANozILLA:**
            1. 📁 Upload an image (JPG, PNG, WEBP)
            2. 🎨 Describe your desired transformation style
            3. 🚀 Click GENERATE TRANSFORMATION
            4. 📥 Download your amazing result!
            
            **Pro Tips:**
            - Be specific in your style descriptions
            - Try different artistic movements
            - Use color and mood keywords
            - Max file size: 10MB
            - Supported formats: JPG, PNG, WEBP
            
            **Example Prompts:**
            - "vibrant anime style with bright colors"
            - "film noir black and white cinematic"
            - "watercolor painting with soft pastels"
            - "cyberpunk neon aesthetic at night"
            """)

            # Add spelling help to help section
            display_spelling_help()

        # System info
        with st.expander("🖥️ SYSTEM INFO"):
            agent_status = "✅ READY" if st.session_state.reactor_agent else "❌ OFFLINE"
            processor_status = "✅ READY" if st.session_state.image_processor else "❌ OFFLINE"

            st.code(f"""
NANozILLA v2.0 - 8BIT EDITION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reactor Agent: {agent_status}
Image Processor: {processor_status}
Errors: {st.session_state.error_count}
Success: {st.session_state.success_count}
Status: {'🔄 PROCESSING' if st.session_state.processing else '✅ READY'}
            """)

    # ========================================================================
    # MAIN CONTENT AREA
    # ========================================================================

    display_pixel_divider()

    # Create two columns for before/after
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📤 ORIGINAL IMAGE")

        if uploaded_file and st.session_state.image_processor:
            try:
                with st.spinner("🖼️ Processing uploaded image..."):
                    image_bytes, format_info = st.session_state.image_processor.process_uploaded_image(
                        uploaded_file)
                    original_image = st.session_state.image_processor.prepare_for_display(
                        image_bytes)

                    if original_image:
                        st.image(original_image, caption="Original Image", use_container_width=True)

                        # Display image info
                        info_box = f"""
                        <div class="status-box">
                        📊 IMAGE ANALYSIS
                        ━━━━━━━━━━━━━━━━━━━━
                        Size: {format_info['width']}x{format_info['height']}
                        Format: {format_info['format']}
                        Mode: {format_info['mode']}
                        File Size: {format_info['file_size_mb']}MB
                        Color: {format_info.get('color_analysis', {}).get('color_mode', 'Unknown')}
                        Grayscale: {format_info.get('color_analysis', {}).get('is_grayscale', False)}
                        </div>
                        """
                        st.markdown(info_box, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")
                st.session_state.error_count += 1
        else:
            st.info("""
            ⚠️ NO IMAGE UPLOADED
            
            Please upload an image from the sidebar to begin your 
            AI-powered transformation journey!
            """)

    with col2:
        st.markdown("### 🎨 GENERATED IMAGE")

        if st.session_state.generated_image and st.session_state.image_processor:
            try:
                generated_image = st.session_state.image_processor.prepare_for_display(
                    st.session_state.generated_image
                )

                if generated_image:
                    st.image(generated_image, caption="AI Transformed", use_container_width=True)

                    # Download button
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG")

                    st.download_button(
                        label="📥 DOWNLOAD TRANSFORMED IMAGE",
                        data=buf.getvalue(),
                        file_name=(
                            f"nanozilla_{st.session_state.uploaded_file_name or 'output'}.png"
                        ),
                        mime="image/png",
                        use_container_width=True
                    )

                    # Display generation info
                    if st.session_state.generation_time:
                        info_box = f"""
                        <div class="status-box">
                        ⏱️ GENERATION COMPLETE
                        ━━━━━━━━━━━━━━━━━━━━━━━━
                        Processing Time: {st.session_state.generation_time}
                        Status: SUCCESSFUL ✓
                        Quality: High
                        </div>
                        """
                        st.markdown(info_box, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error displaying generated image: {str(e)}")
                st.session_state.error_count += 1
        else:
            st.info("""
            ⚠️ NO GENERATED IMAGE
            
            Your AI-transformed masterpiece will appear here after 
            you click the GENERATE button!
            """)

    # ========================================================================
    # GENERATION LOGIC
    # ========================================================================
    if generate_btn:
        # Validation checks
        if not uploaded_file:
            st.error("""
            ⚠️ ERROR: No image uploaded!
            
            Please upload an image file to begin transformation.
            """)
            st.session_state.error_count += 1
            return

        if not style_prompt:
            st.error("""
            ⚠️ ERROR: No style prompt provided!
            
            Please describe how you want to transform your image.
            """)
            st.session_state.error_count += 1
            return

        # Validate prompt
        try:
            validate_prompt(style_prompt)
        except Exception as e:
            st.error(f"⚠️ ERROR: {str(e)}")
            st.session_state.error_count += 1
            return

        # Check if components are available
        if not st.session_state.reactor_agent:
            st.error("""
            ❌ CRITICAL: Reactor Agent not available!
            
            Please check your API configuration and try again.
            """)
            return

        if not st.session_state.image_processor:
            st.error("""
            ❌ CRITICAL: Image Processor not available!
            
            Please refresh the page and try again.
            """)
            return

        # Set processing state
        st.session_state.processing = True

        try:
            # Process image
            with st.spinner("📊 Processing image data..."):
                image_bytes, image_info = st.session_state.image_processor.process_uploaded_image(
                    uploaded_file)
                time.sleep(0.5)  # Visual feedback

            # Generate transformation
                progress_text = (
                    "🔄 NANozILLA Reactor Agent is transforming your image..."
                )

            with st.spinner(progress_text):
                start_time = time.time()

                # Show progress bar
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)  # Faster progress for better UX
                    progress_bar.progress(i + 1)

                # Execute colorization
                generated_bytes = st.session_state.reactor_agent.execute_colorization(
                    image_bytes=image_bytes,
                    style_prompt=style_prompt,
                    quality=quality,
                    safety_level=safety_level,
                    retry_attempts=retry_attempts
                )

                end_time = time.time()
                generation_time = f"{end_time - start_time:.2f}s"

            # Store results
            st.session_state.generated_image = generated_bytes
            st.session_state.generation_time = generation_time
            st.session_state.success_count += 1
            st.session_state.processing = False

            # Success message
            success_msg = f"""
            <div class="status-box">
            ✅ TRANSFORMATION COMPLETE!
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━
            Generation Time: {generation_time}
            Style Applied: {style_prompt[:50]}...
            Status: SUCCESS ✓
            </div>
            """
            st.markdown(success_msg, unsafe_allow_html=True)

            # Auto-scroll to result
            st.balloons()
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.session_state.processing = False
            st.session_state.error_count += 1
            st.session_state.last_error = str(e)

            st.error(f"""
            ❌ TRANSFORMATION FAILED!
            
            Error: {str(e)}
            
            💡 Troubleshooting Tips:
            • Try a simpler style prompt
            • Check your internet connection
            • Verify the image format
            • Wait a moment and try again
            """)

            with st.expander("🔍 Technical Details"):
                st.code(traceback.format_exc())

    # ========================================================================
    # FOOTER
    # ========================================================================
    display_pixel_divider()

    footer_html = """
    <div class="status-box" style="text-align: center;">
    ╔════════════════════════════════════════════════════════════════╗
    ║           🎮 NANOZILLA AI COLORIZER v2.0 - 8BIT EDITION 🎮    ║
    ║              Powered by Google Gemini & Streamlit             ║
    ║           Transform Your Images with AI Magic! ✨            ║
    ╚════════════════════════════════════════════════════════════════╝
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("""
        🚨 CRITICAL ERROR: Application Crashed!
        
        The NANozILLA reactor has encountered a critical error.
        Please try refreshing the page.
        """)

        with st.expander("🚑 Emergency Technical Details"):
            st.code(traceback.format_exc())

        if st.button("🔄 EMERGENCY RESTART"):
            st.session_state.clear()
            st.rerun()
