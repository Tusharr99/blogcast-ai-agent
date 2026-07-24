import os
import requests
import traceback
from bs4 import BeautifulSoup
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.models.openai import OpenAIChat
from elevenlabs import ElevenLabs
import openai
import streamlit as st

# Streamlit Setup
st.set_page_config(page_title="🎙️ BlogCast AI", page_icon="🎙️")
st.title("🎙️ BlogCast AI")
st.markdown("*Convert any blog post or article into a podcast episode powered by AI.*")

# API Keys (Runtime Input)
st.sidebar.header("🔑 API Keys")
openai_key = st.sidebar.text_input("OpenAI API Key", type="password")
elevenlabs_key = st.sidebar.text_input("ElevenLabs API Key", type="password")
firecrawl_key = st.sidebar.text_input("Firecrawl API Key (Optional)", type="password")

# Blog URL Input
url = st.text_input("Enter Blog URL:", "")

def scrape_blog_content(blog_url: str, fc_key: str = "") -> str:
    """Scrapes blog content using Firecrawl if available, or falls back to requests + BeautifulSoup."""
    scraped_text = ""
    
    # 1. Try Firecrawl if key is provided
    if fc_key:
        try:
            from firecrawl import FirecrawlApp
            app = FirecrawlApp(api_key=fc_key)
            try:
                res = app.scrape(blog_url, formats=['markdown'])
            except Exception:
                res = app.scrape_url(blog_url)

            if hasattr(res, 'markdown') and res.markdown:
                scraped_text = res.markdown
            elif isinstance(res, dict) and res.get('markdown'):
                scraped_text = res['markdown']
        except Exception as fc_err:
            st.warning(f"Firecrawl issue ({fc_err}). Using standard web scraper fallback...")

    # 2. Fallback to requests + BeautifulSoup if Firecrawl didn't return text
    if not scraped_text:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(blog_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Clean out non-content tags
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            element.decompose()

        article = soup.find('article') or soup.find('main') or soup.body
        raw_text = article.get_text(separator='\n') if article else soup.get_text(separator='\n')
        
        lines = (line.strip() for line in raw_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        scraped_text = '\n'.join(chunk for chunk in chunks if chunk)

    return scraped_text[:8000]

# Generate Button
if st.button("🎙️ Generate Podcast", disabled=not all([openai_key, elevenlabs_key])):
    if not url.strip():
        st.warning("Please enter a blog URL")
    else:
        # Clean API keys
        clean_openai_key = openai_key.strip()
        clean_elevenlabs_key = elevenlabs_key.strip()
        clean_firecrawl_key = firecrawl_key.strip()

        os.environ["OPENAI_API_KEY"] = clean_openai_key

        # Step 1: Scrape Content
        with st.spinner("Step 1/3: Scraping blog content..."):
            try:
                blog_text = scrape_blog_content(url.strip(), clean_firecrawl_key)
            except Exception as e:
                st.error(f"❌ Scraping Error: Could not fetch content from the URL. Details: {e}")
                st.stop()

        if not blog_text:
            st.error("❌ Scraping Error: Failed to extract text from the provided URL.")
            st.stop()

        # Step 2: Summarize Content with Agno Agent & OpenAI
        with st.spinner("Step 2/3: Summarizing blog content with OpenAI..."):
            try:
                agent = Agent(
                    name="Blog Summarizer",
                    model=OpenAIChat(id="gpt-4o", api_key=clean_openai_key),
                    instructions=[
                        "You are a professional podcast host scriptwriter.",
                        "Create a concise, engaging, and conversational summary (max 2000 characters) suitable for a podcast based on the provided blog content.",
                        "Capture the key takeaways and main discussion points naturally."
                    ],
                )

                response: RunOutput = agent.run(f"Create a podcast summary for the following blog content:\n\n{blog_text}")
                summary = response.content if hasattr(response, 'content') else str(response)
            except openai.AuthenticationError as auth_err:
                st.error("🔑 OpenAI Key Error: The OpenAI API key you entered is invalid or expired. Please check your OpenAI key.")
                st.stop()
            except Exception as e:
                err_str = str(e)
                if "401" in err_str or "invalid_api_key" in err_str or "incorrect api key" in err_str.lower():
                    st.error("🔑 OpenAI Key Error: Invalid OpenAI API Key.")
                else:
                    st.error(f"❌ Summarization Error: {e}")
                st.stop()

        if not summary:
            st.error("❌ Summarization Error: Failed to generate summary.")
            st.stop()

        # Step 3: Generate Audio with ElevenLabs
        with st.spinner("Step 3/3: Generating audio podcast with ElevenLabs..."):
            try:
                client = ElevenLabs(api_key=clean_elevenlabs_key)
                
                audio_generator = client.text_to_speech.convert(
                    text=summary,
                    voice_id="JBFqnCBsd6RMkjVDRZzb",
                    model_id="eleven_multilingual_v2"
                )
                
                audio_chunks = []
                for chunk in audio_generator:
                    if chunk:
                        audio_chunks.append(chunk)
                audio_bytes = b"".join(audio_chunks)
            except Exception as e:
                err_str = str(e)
                if "401" in err_str or "invalid_api_key" in err_str or "unauthorized" in err_str.lower():
                    st.error("🔑 ElevenLabs Key Error: The ElevenLabs API key you entered is invalid or expired. Please check your ElevenLabs key.")
                else:
                    st.error(f"❌ ElevenLabs Audio Error: {e}")
                st.stop()

        # UI Outputs
        st.success("Podcast generated successfully! 🎧")
        st.audio(audio_bytes, format="audio/mp3")
        
        st.download_button(
            "Download Podcast",
            audio_bytes,
            "podcast.mp3",
            "audio/mp3"
        )
        
        with st.expander("📄 Podcast Summary"):
            st.write(summary)
