"""
Text-to-Speech service using Azure Speech Services
Handles audio generation for story pages
"""
import os
from typing import Optional, Tuple
from fastapi import HTTPException

# Optional import - allows server to start even if package is not installed
try:
    import azure.cognitiveservices.speech as speechsdk
    SPEECH_SDK_AVAILABLE = True
except ImportError:
    SPEECH_SDK_AVAILABLE = False
    speechsdk = None

# Lazy initialization of Azure Speech client
_speech_config = None


def get_azure_speech_config():
    """Get or create Azure Speech config (lazy initialization)"""
    global _speech_config
    if not SPEECH_SDK_AVAILABLE:
        return None
    
    if _speech_config is None:
        speech_key = os.getenv("AZURE_SPEECH_KEY")
        speech_region = os.getenv("AZURE_SPEECH_REGION")
        
        if speech_key and speech_region:
            _speech_config = speechsdk.SpeechConfig(
                subscription=speech_key,
                region=speech_region
            )
            # Set voice name (default to a child-friendly voice)
            voice_name = os.getenv("AZURE_SPEECH_VOICE_NAME", "en-US-AriaNeural")
            _speech_config.speech_synthesis_voice_name = voice_name
    return _speech_config


class TTSService:
    """Service for generating speech audio using Azure Speech Services"""
    
    @staticmethod
    def synthesize_text(text: str, language: str = "en-US") -> bytes:
        """
        Synthesize text to speech audio
        
        Args:
            text: Text to convert to speech
            language: Language code (e.g., "en-US", "zh-CN")
        
        Returns:
            Audio data as bytes (WAV format)
        
        Raises:
            HTTPException: If TTS generation fails
        """
        if not SPEECH_SDK_AVAILABLE:
            raise HTTPException(
                status_code=500,
                detail="Azure Speech SDK not installed. Please install it with: pip install azure-cognitiveservices-speech"
            )
        
        speech_config = get_azure_speech_config()
        
        if not speech_config:
            raise HTTPException(
                status_code=500,
                detail="Azure Speech Services not configured. Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables."
            )
        
        # Override voice based on language if needed
        voice_name = TTSService._get_voice_for_language(language)
        speech_config.speech_synthesis_voice_name = voice_name
        
        # Create synthesizer without audio config to get audio data directly
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        try:
            # Synthesize text to speech
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Get audio data from result
                audio_data = result.audio_data
                return bytes(audio_data)
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speechsdk.CancellationDetails(result)
                error_msg = f"Speech synthesis canceled: {cancellation_details.reason}"
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" Error details: {cancellation_details.error_details}"
                raise HTTPException(
                    status_code=500,
                    detail=error_msg
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Speech synthesis failed: {result.reason}"
                )
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise HTTPException(
                    status_code=401,
                    detail="Azure Speech Services authentication failed. Please check your AZURE_SPEECH_KEY and AZURE_SPEECH_REGION configuration."
                )
            elif "429" in error_str or "rate limit" in error_str.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Azure Speech Services rate limit exceeded. Please try again in a few minutes."
                )
            elif "quota" in error_str.lower():
                raise HTTPException(
                    status_code=402,
                    detail="Azure Speech Services quota exceeded. Please check your Azure account billing."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Azure Speech Services error: {str(e)}"
                )
    
    @staticmethod
    def _get_voice_for_language(language: str) -> str:
        """
        Get appropriate voice name for language
        
        Args:
            language: Language code (e.g., "en-US", "zh-CN", "en")
        
        Returns:
            Voice name for Azure Speech Services
        """
        # Default voice mapping
        voice_mapping = {
            "en": "en-US-AriaNeural",  # Friendly, warm female voice
            "en-US": "en-US-AriaNeural",
            "en-GB": "en-GB-SoniaNeural",
            "zh": "zh-CN-XiaoxiaoNeural",  # Chinese female voice
            "zh-CN": "zh-CN-XiaoxiaoNeural",
            "zh-TW": "zh-TW-HsiaoYuNeural",
            "es": "es-ES-ElviraNeural",
            "es-ES": "es-ES-ElviraNeural",
            "fr": "fr-FR-DeniseNeural",
            "fr-FR": "fr-FR-DeniseNeural",
            "de": "de-DE-KatjaNeural",
            "de-DE": "de-DE-KatjaNeural",
            "ja": "ja-JP-NanamiNeural",
            "ja-JP": "ja-JP-NanamiNeural",
            "ko": "ko-KR-SunHiNeural",
            "ko-KR": "ko-KR-SunHiNeural",
        }
        
        # Get custom voice from env or use mapping
        custom_voice = os.getenv("AZURE_SPEECH_VOICE_NAME")
        if custom_voice:
            return custom_voice
        
        # Normalize language code
        lang_lower = language.lower()
        if lang_lower in voice_mapping:
            return voice_mapping[lang_lower]
        
        # Try to match by prefix (e.g., "en" matches "en-US")
        for lang_code, voice in voice_mapping.items():
            if lang_lower.startswith(lang_code.split("-")[0]):
                return voice
        
        # Default to English friendly voice
        return "en-US-AriaNeural"
    
    @staticmethod
    def save_audio(audio_bytes: bytes, story_id: str, page_number: int) -> str:
        """
        Save audio bytes to disk
        
        Args:
            audio_bytes: Audio data as bytes (WAV format)
            story_id: Story identifier
            page_number: Page number (1-indexed)
        
        Returns:
            Relative path to the saved audio file
        """
        # Create audio directory structure: stories/audio/{story_id}/
        audio_dir = os.path.join("stories", "audio", story_id)
        os.makedirs(audio_dir, exist_ok=True)
        
        # Save audio as WAV file
        audio_filename = f"{page_number}.wav"
        audio_path = os.path.join(audio_dir, audio_filename)
        
        try:
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)
            return os.path.join("audio", story_id, audio_filename)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save audio: {str(e)}"
            )
    
    @staticmethod
    def get_audio_path(story_id: str, page_number: int) -> str:
        """
        Get the file path for an audio file
        
        Args:
            story_id: Story identifier
            page_number: Page number (1-indexed)
        
        Returns:
            Relative path to the audio file
        """
        return os.path.join("audio", story_id, f"{page_number}.wav")
    
    @staticmethod
    def audio_exists(story_id: str, page_number: int) -> bool:
        """
        Check if audio file exists
        
        Args:
            story_id: Story identifier
            page_number: Page number (1-indexed)
        
        Returns:
            True if audio file exists, False otherwise
        """
        audio_path = os.path.join("stories", "audio", story_id, f"{page_number}.wav")
        return os.path.exists(audio_path)

