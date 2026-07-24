## 🎙️ BlogCast AI
**BlogCast AI** is a Streamlit-based application that allows users to convert any blog post or online article into a podcast. The app uses OpenAI's GPT-4o model for podcast scriptwriting, Firecrawl and BeautifulSoup for web scraping, and ElevenLabs API for high-quality audio synthesis.

## Features

- **Blog Scraping**: Scrapes the full content of any public blog URL using Firecrawl API.

- **Summary Generation**: Creates an engaging and concise summary of the blog (within 2000 characters) using OpenAI GPT-4.

- **Podcast Generation**: Converts the summary into an audio podcast using the ElevenLabs voice API.

- **API Key Integration**: Requires OpenAI, Firecrawl, and ElevenLabs API keys to function, entered securely via the sidebar.

## Setup

### Requirements 

1. **API Keys**:
    - **OpenAI API Key**: Sign up at OpenAI to obtain your API key.

    - **ElevenLabs API Key**: Get your ElevenLabs API key from ElevenLabs.

    - **Firecrawl API Key**: Get your Firecrawl API key from Firecrawl.

2. **Python 3.8+**: Ensure you have Python 3.8 or higher installed.

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/Shubhamsaboo/awesome-llm-apps
   cd starter_ai_agents/ai_blogcast_agent
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
### Running the App

1. Start the Streamlit app:
   ```bash
   streamlit run blogcast_ai_agent.py
   ```

2. In the app interface:
    - Enter your OpenAI, ElevenLabs, and Firecrawl API keys in the sidebar.

    - Input the blog URL you want to convert.

    - Click "🎙️ Generate Podcast".

    - Listen to the generated podcast or download it.