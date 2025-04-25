# Legal Assistant AI

A powerful AI-powered legal assistant that helps users understand legal documents, find lawyers, and navigate legal procedures. Built with Azure OpenAI, Chainlit, and various Azure services.

## Features

### 1. Multi-language Support

- Automatic language detection
- Real-time translation of queries and responses
- Support for all major languages

### 2. Contract Analysis

- Break down complex legal terms
- Highlight important clauses
- Identify potential risks
- Explain rights and obligations
- Provide document checklists

### 3. Legal Form Assistance

- Guide through form filling
- Explain required documentation
- Provide step-by-step instructions
- Highlight common mistakes to avoid
- Access to downloadable forms

### 4. Lawyer Recommendations

- Location-based lawyer search
- Specialization matching
- Detailed lawyer profiles including:
  - Contact information
  - Ratings and reviews
  - Operating hours
  - Price levels
  - Websites
  - Top client reviews
- Support for multiple legal specializations

### 5. Interactive UI

- User-friendly chat interface
- Quick action buttons
- Document previews
- Context-aware responses
- Progress tracking

## Technology Stack

- **Azure OpenAI**: For natural language processing and generation
- **Azure Translator**: For multi-language support
- **Azure Blob Storage**: For document management
- **Google Places API**: For lawyer recommendations
- **Chainlit**: For the chat interface
- **Python**: Core programming language

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Azure account with OpenAI access
- Google Cloud account with Places API enabled
- Azure Blob Storage account

### 2. Azure OpenAI Setup

1. Create an Azure OpenAI resource in the Azure portal
2. Deploy a model:
   - Go to Azure OpenAI Studio
   - Click on "Deployments"
   - Create a new deployment
   - Select model (e.g., "gpt-35-turbo" or "gpt-4")
   - Give it a deployment name (you'll need this for DEPLOYMENT_NAME)
3. Note down:
   - Endpoint URL
   - API Key
   - Deployment name

### 3. Environment Setup

```bash
# Clone the repository
git clone [repository-url]
cd [repository-name]

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration

You can authenticate with Azure OpenAI in two ways:

#### Option 1: Using Azure CLI (Recommended for development)

1. Install Azure CLI and login:

```bash
# Install Azure CLI (if not already installed)
winget install -e --id Microsoft.AzureCLI   # For Windows
brew install azure-cli                      # For macOS
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash  # For Ubuntu/Debian

# Login to Azure
az login
```

2. Install required Python packages:

```bash
pip install azure-identity openai
```

3. Use this code to authenticate:

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

# Get Azure credentials
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

# Create OpenAI client
client = AzureOpenAI(
    api_version="2024-02-15-preview",
    azure_endpoint="https://{your-resource-name}.openai.azure.com/",
    azure_ad_token_provider=token_provider
)
```

#### Option 2: Using Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Azure OpenAI Configuration
ENDPOINT_URL=your-azure-openai-endpoint        # e.g., https://your-resource.openai.azure.com/
DEPLOYMENT_NAME=your-model-deployment-name     # e.g., gpt-35-turbo or your custom deployment name
AZURE_OPENAI_API_KEY=your-api-key             # The API key from Azure OpenAI resource

# Azure Translator Configuration
AZURE_TRANSLATOR_ENDPOINT=your-translator-endpoint
AZURE_TRANSLATOR_KEY=your-translator-key

# Azure Blob Storage Configuration
AZURE_BLOB_CONNECTION_STRING=your-blob-connection-string
AZURE_BLOB_CONTAINER=your-container-name

# Google Maps Configuration
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### 5. Running the Application

```bash
chainlit run app.py
```

The application will be available at `http://localhost:8000`

## Project Structure

```
├── app.py                 # Main application file
├── prompts/              # Prompt templates
│   ├── contract_analysis.txt
│   ├── form_guidance.txt
│   └── lawyer_recommendation.txt
├── public/              # Static assets
│   ├── images.png
│   ├── write.svg
│   └── research.svg
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Usage Examples

1. **Contract Analysis**

   ```
   User: Can you help me understand this employment contract?
   Assistant: I'll help you analyze the contract. Please share the contract text or specific sections you'd like to understand.
   ```

2. **Form Assistance**

   ```
   User: How do I fill out a divorce petition?
   Assistant: I'll guide you through the divorce petition form step by step...
   ```

3. **Lawyer Recommendation**
   ```
   User: I need a property lawyer in Mumbai
   Assistant: I'll help you find qualified property lawyers in Mumbai. Here are some recommendations...
   ```

## Troubleshooting

### Common Issues

1. **Azure OpenAI Connection Issues**

   - Verify your DEPLOYMENT_NAME matches exactly with your Azure OpenAI deployment
   - Check if your API key is correct and not expired
   - Ensure your endpoint URL includes 'https://'

2. **Language Detection Issues**

   - Make sure Azure Translator service is properly configured
   - Check if the language codes are supported

3. **Lawyer Search Issues**
   - Verify Google Maps API key has Places API enabled
   - Check if the location provided is valid
   - Ensure proper internet connectivity

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Azure OpenAI team for the powerful language models
- Chainlit team for the excellent chat interface framework
- Google Maps Platform for location services
- All contributors and users of this project

## Support

For support, please open an issue in the repository or contact the maintainers.
