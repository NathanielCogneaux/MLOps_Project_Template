import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style
import zipfile

init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:8005"
API_PREFIX = "/smart_pricing_api/v2"
PROPERTY_IDS = [1, 6]
SCRAP_TYPES = ["A", "B"]
DEFAULT_TIMEZONE = "Asia/Seoul"

# Generate current timestamp in the format the API expects
current_time = pd.Timestamp.now(tz=DEFAULT_TIMEZONE)
SAMPLE_DATE = current_time.isoformat()

AI_MODELS = ["baseline", "optimized_baseline"]

# Output configuration
OUTPUT_DIR = "api_examples"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
FULL_OUTPUT_DIR = f"{OUTPUT_DIR}_{TIMESTAMP}"

def print_header(title, color=Fore.CYAN):
    """Print a beautifully formatted header"""
    width = 100
    print(f"\n{color}{'=' * width}{Style.RESET_ALL}")
    print(f"{color}{title.center(width)}{Style.RESET_ALL}")
    print(f"{color}{'=' * width}{Style.RESET_ALL}")

def print_status(message, color=Fore.WHITE):
    """Print status message"""
    print(f"{color}{message}{Style.RESET_ALL}")

def create_directory_structure():
    """Create the directory structure for organizing API examples"""
    directories = [
        "connection",
        "root",
        "health",
        "updates",
        "data/properties",
        "data/competitor_prices",
        "data/ai_prices", 
        "data/market_stats",
        "data/events"
    ]
    
    base_path = Path(FULL_OUTPUT_DIR)
    base_path.mkdir(exist_ok=True)
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print_status(f"📁 Created directory structure in: {FULL_OUTPUT_DIR}", Fore.GREEN)
    return base_path

def sanitize_filename(filename):
    """Sanitize filename for cross-platform compatibility"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def save_response_data(category, endpoint_name, method, url, params=None, payload=None, 
                      response_data=None, status_code=None, error_message=None, 
                      description="", base_path=None):
    """Save response data and request details to organized files"""
    
    safe_name = sanitize_filename(endpoint_name.lower().replace(' ', '_').replace('-', '_'))
    
    category_path = base_path / category
    category_path.mkdir(exist_ok=True)
    
    request_info = {
        "endpoint_name": endpoint_name,
        "method": method.upper(),
        "url": url,
        "description": description,
        "timestamp": datetime.now().isoformat(),
        "parameters": params,
        "payload": payload,
        "status_code": status_code
    }
    
    request_file = category_path / f"{safe_name}_request.json"
    with open(request_file, 'w', encoding='utf-8') as f:
        json.dump(request_info, f, indent=2, ensure_ascii=False)
    
    if response_data is not None:
        response_file = category_path / f"{safe_name}_response.json"
        with open(response_file, 'w', encoding='utf-8') as f:
            if isinstance(response_data, str):
                try:
                    response_data = json.loads(response_data)
                except json.JSONDecodeError:
                    # If it's not JSON, save as text in a JSON wrapper
                    response_data = {"raw_response": response_data}
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        print_status(f"💾 Saved: {category}/{safe_name}", Fore.BLUE)
    
    if error_message:
        error_info = {
            "error": error_message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
        error_file = category_path / f"{safe_name}_error.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_info, f, indent=2, ensure_ascii=False)
        print_status(f"⚠️  Error saved: {category}/{safe_name}", Fore.YELLOW)
    
    summary_file = category_path / f"{safe_name}_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Endpoint: {endpoint_name}\n")
        f.write(f"Method: {method.upper()}\n")
        f.write(f"URL: {url}\n")
        f.write(f"Description: {description}\n")
        f.write(f"Status Code: {status_code}\n")
        if params:
            f.write(f"Parameters: {json.dumps(params, indent=2)}\n")
        if payload:
            f.write(f"Payload: {json.dumps(payload, indent=2)}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")

def make_request_and_save(method, url, category, endpoint_name, description="", 
                         payload=None, params=None, base_path=None):
    """Enhanced function to make requests, display results, and save to files"""
    try:
        print_status(f"🚀 Testing: {endpoint_name}", Fore.MAGENTA)
        
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=payload, timeout=10)
        else:
            error_msg = f"Unsupported method: {method}"
            print_status(f"❌ {error_msg}", Fore.RED)
            save_response_data(category, endpoint_name, method, url, params, payload,
                             None, None, error_msg, description, base_path)
            return
        
        if response.status_code == 200:
            status_color = Fore.GREEN
            status_icon = "✅"
        elif response.status_code in [400, 401, 403, 404]:
            status_color = Fore.YELLOW  
            status_icon = "⚠️"
        else:
            status_color = Fore.RED
            status_icon = "❌"
            
        print_status(f"{status_icon} {endpoint_name}: {response.status_code}", status_color)
        
        response_data = None
        error_message = None
        
        if response.status_code == 200:
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text
        else:
            error_message = response.text
            try:
                error_data = response.json()
                response_data = error_data
            except:
                response_data = {"error_text": response.text}
        
        save_response_data(category, endpoint_name, method, url, params, payload,
                          response_data, response.status_code, error_message, 
                          description, base_path)
        
    except requests.exceptions.ConnectionError:
        error_msg = f"Connection Error: Could not connect to {url}"
        print_status(f"🔌 {error_msg}", Fore.RED)
        save_response_data(category, endpoint_name, method, url, params, payload,
                          None, None, error_msg, description, base_path)
    except requests.exceptions.Timeout:
        error_msg = "Timeout Error: Request took longer than 10 seconds"
        print_status(f"⏰ {error_msg}", Fore.RED)
        save_response_data(category, endpoint_name, method, url, params, payload,
                          None, None, error_msg, description, base_path)
    except Exception as e:
        error_msg = f"Request failed: {str(e)}"
        print_status(f"💥 {error_msg}", Fore.RED)
        save_response_data(category, endpoint_name, method, url, params, payload,
                          None, None, error_msg, description, base_path)

def create_readme_file(base_path):
    """Create a comprehensive README file explaining the folder structure"""
    readme_content = f"""# Smart Pricing API v2 - Example Responses

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Base URL: {BASE_URL}
API Prefix: {API_PREFIX}

## Folder Structure

```
{FULL_OUTPUT_DIR}/
├── connection/              # Basic connection tests
├── root/                    # Root endpoint responses
├── health/                  # Health check endpoints
├── updates/                 # Update status endpoints
└── data/                    # Main data endpoints
    ├── properties/          # Properties configuration
    ├── competitor_prices/   # Competitor pricing data
    ├── ai_prices/          # AI price predictions
    ├── market_stats/       # Market statistics
    └── events/             # Events data
```

## File Types

For each endpoint, you'll find:
- `*_request.json`: Request details (method, URL, parameters, payload)
- `*_response.json`: Response data (if successful)
- `*_error.json`: Error information (if failed)
- `*_summary.txt`: Quick text summary

## Test Configuration

- Property IDs tested: {PROPERTY_IDS}
- Scrap Types: {SCRAP_TYPES} (A=hourly, B=daily)
- AI Models: {AI_MODELS}
- Sample Date: {SAMPLE_DATE}

## Endpoint Categories

### Connection
- Basic server connectivity test

### Root  
- API root information and version

### Health
- Comprehensive health check
- Readiness check (load balancers)
- Liveness check (Kubernetes)

### Updates
- Latest update timestamps by scrap type
- Overall update status

### Data - Properties
- All available properties with configurations

### Data - Competitor Prices
- Competitor pricing data by property and scrap type

### Data - AI Prices  
- AI price predictions by property, scrap type, and model

### Data - Market Stats
- Market statistics by property

### Data - Events
- Events data by property

## Usage

1. Review the `*_summary.txt` files for quick endpoint overviews
2. Check `*_request.json` files to understand request formats
3. Examine `*_response.json` files to see successful response structures
4. Look at `*_error.json` files to understand error formats

## Notes

- All timestamps are in {DEFAULT_TIMEZONE} timezone
- Responses may be truncated if extremely large
- Error responses are preserved for debugging purposes
"""
    
    readme_file = base_path / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print_status(f"📖 Created README.md", Fore.GREEN)

def create_zip_archive(base_path):
    """Create a zip archive of all the examples"""
    zip_filename = f"{FULL_OUTPUT_DIR}.zip"
    
    print_status(f"📦 Creating zip archive: {zip_filename}", Fore.CYAN)
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in base_path.rglob('*'):
            if file_path.is_file():
                # Create relative path for the zip
                relative_path = file_path.relative_to(base_path.parent)
                zipf.write(file_path, relative_path)
    
    print_status(f"✅ Zip archive created: {zip_filename}", Fore.GREEN)
    return zip_filename

def main():
    """Main function to run all API tests and save organized examples"""
    print_header("🚀 SMART PRICING API v2 - RESPONSE COLLECTOR", Fore.CYAN)
    print_status(f"Output Directory: {FULL_OUTPUT_DIR}", Fore.WHITE)
    print_status(f"Base URL: {BASE_URL}", Fore.WHITE)
    print_status(f"Sample Date: {SAMPLE_DATE}", Fore.WHITE)
    
    # Create directory structure
    base_path = create_directory_structure()
    
    # =============================================================================
    # CONNECTION TEST
    # =============================================================================
    
    print_header("🔍 CONNECTION TEST", Fore.MAGENTA)
    make_request_and_save(
        "GET", BASE_URL, "connection", "Server Connection Test",
        "Basic connectivity test to ensure server is accessible",
        base_path=base_path
    )
    
    # =============================================================================
    # DEBUGGING - OPENAPI SCHEMA
    # =============================================================================
    
    print_header("🛠️  API SCHEMA", Fore.MAGENTA)
    make_request_and_save(
        "GET", f"{BASE_URL}/openapi.json", "root", "OpenAPI Schema",
        "OpenAPI schema showing all registered endpoints and their specifications",
        base_path=base_path
    )
    
    # =============================================================================
    # ROOT ENDPOINT
    # =============================================================================
    
    print_header("🏠 ROOT ENDPOINTS", Fore.BLUE)
    make_request_and_save(
        "GET", f"{BASE_URL}/", "root", "API Root",
        "API root information, version, and basic metadata",
        base_path=base_path
    )
    
    # =============================================================================
    # HEALTH CHECK ENDPOINTS
    # =============================================================================
    
    print_header("🏥 HEALTH CHECK ENDPOINTS", Fore.GREEN)
    
    health_endpoints = [
        ("Comprehensive Health Check", f"{BASE_URL}{API_PREFIX}/health/", 
         "Comprehensive health status including system metrics and path checks"),
        ("Readiness Check", f"{BASE_URL}{API_PREFIX}/health/ready", 
         "Simple readiness check for load balancers"),
        ("Liveness Check", f"{BASE_URL}{API_PREFIX}/health/live", 
         "Simple liveness check for Kubernetes")
    ]
    
    for name, url, desc in health_endpoints:
        make_request_and_save("GET", url, "health", name, desc, base_path=base_path)
    
    # =============================================================================
    # UPDATE STATUS ENDPOINTS
    # =============================================================================
    
    print_header("📊 UPDATE STATUS ENDPOINTS", Fore.CYAN)
    
    # Latest updates by scrap type
    for scrap_type in SCRAP_TYPES:
        type_desc = "hourly" if scrap_type == "A" else "daily"
        make_request_and_save(
            "GET", f"{BASE_URL}{API_PREFIX}/updates/latest/{scrap_type}",
            "updates", f"Latest Updates Type {scrap_type}",
            f"Latest update timestamps for {type_desc} scrap type {scrap_type}",
            base_path=base_path
        )
    
    # Overall status
    make_request_and_save(
        "GET", f"{BASE_URL}{API_PREFIX}/updates/status",
        "updates", "Overall Update Status",
        "Overall update status for both scrap types A and B",
        base_path=base_path
    )
    
    # =============================================================================
    # DATA ENDPOINTS - PROPERTIES
    # =============================================================================
    
    print_header("💾 PROPERTIES DATA", Fore.YELLOW)
    make_request_and_save(
        "GET", f"{BASE_URL}{API_PREFIX}/data/properties",
        "data/properties", "Properties Configuration",
        "All available properties with their configurations and metadata",
        base_path=base_path
    )
    
    # =============================================================================
    # DATA ENDPOINTS - COMPETITOR PRICES
    # =============================================================================
    
    print_header("💰 COMPETITOR PRICES", Fore.RED)
    for property_id in PROPERTY_IDS:
        for scrap_type in SCRAP_TYPES:
            type_desc = "hourly" if scrap_type == "A" else "daily"
            params = {
                "date": SAMPLE_DATE,
                "scrap_type": scrap_type
            }
            make_request_and_save(
                "GET", f"{BASE_URL}{API_PREFIX}/data/comp-prices/{property_id}",
                "data/competitor_prices", f"Competitor Prices P{property_id} Type{scrap_type}",
                f"Competitor prices for property {property_id} with {type_desc} scrap type {scrap_type}",
                params=params, base_path=base_path
            )
    
    # =============================================================================
    # DATA ENDPOINTS - AI PRICES
    # =============================================================================
    
    print_header("🤖 AI PRICE PREDICTIONS", Fore.MAGENTA)
    for property_id in PROPERTY_IDS:
        for scrap_type in SCRAP_TYPES:
            for model in AI_MODELS:
                type_desc = "hourly" if scrap_type == "A" else "daily"
                params = {
                    "date": SAMPLE_DATE,
                    "model": model,
                    "scrap_type": scrap_type
                }
                make_request_and_save(
                    "GET", f"{BASE_URL}{API_PREFIX}/data/ai-prices/{property_id}",
                    "data/ai_prices", f"AI Prices P{property_id} Type{scrap_type} Model{model}",
                    f"AI price predictions for property {property_id}, {type_desc} scrap type, using {model} model",
                    params=params, base_path=base_path
                )
    
    # =============================================================================
    # DATA ENDPOINTS - MARKET STATS
    # =============================================================================
    
    print_header("📈 MARKET STATISTICS", Fore.BLUE)
    for property_id in PROPERTY_IDS:
        params = {"date": SAMPLE_DATE}
        make_request_and_save(
            "GET", f"{BASE_URL}{API_PREFIX}/data/market-stats/{property_id}",
            "data/market_stats", f"Market Statistics P{property_id}",
            f"Market statistics and analytics for property {property_id}",
            params=params, base_path=base_path
        )
    
    # =============================================================================
    # DATA ENDPOINTS - EVENTS
    # =============================================================================
    
    print_header("🎭 EVENTS DATA", Fore.GREEN)
    for property_id in PROPERTY_IDS:
        params = {"date": SAMPLE_DATE}
        make_request_and_save(
            "GET", f"{BASE_URL}{API_PREFIX}/data/events/{property_id}",
            "data/events", f"Events P{property_id}",
            f"Events and calendar data affecting property {property_id}",
            params=params, base_path=base_path
        )
    
    # =============================================================================
    # FINALIZATION
    # =============================================================================
    
    print_header("📝 CREATING DOCUMENTATION", Fore.CYAN)
    
    # Create README
    create_readme_file(base_path)
    
    # Create summary statistics
    total_files = len(list(base_path.rglob('*.json'))) + len(list(base_path.rglob('*.txt')))
    total_endpoints = len(list(base_path.rglob('*_request.json')))
    
    summary_file = base_path / "SUMMARY.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Smart Pricing API v2 - Test Summary\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total Endpoints Tested: {total_endpoints}\n")
        f.write(f"Total Files Generated: {total_files}\n")
        f.write(f"Base URL: {BASE_URL}\n")
        f.write(f"API Prefix: {API_PREFIX}\n")
        f.write(f"Test Date: {SAMPLE_DATE}\n")
        f.write(f"Properties: {PROPERTY_IDS}\n")
        f.write(f"Scrap Types: {SCRAP_TYPES}\n")
        f.write(f"AI Models: {AI_MODELS}\n")
    
    # Create zip archive
    zip_file = create_zip_archive(base_path)
    
    print_header("✅ COLLECTION COMPLETE", Fore.GREEN)
    print_status(f"📊 Total endpoints tested: {total_endpoints}", Fore.CYAN)
    print_status(f"📁 Files generated: {total_files}", Fore.CYAN)
    print_status(f"📂 Output directory: {FULL_OUTPUT_DIR}", Fore.CYAN)
    print_status(f"📦 Zip archive: {zip_file}", Fore.CYAN)
    print_status(f"📖 Documentation: {FULL_OUTPUT_DIR}/README.md", Fore.CYAN)
    
    return base_path, zip_file

if __name__ == "__main__":
    try:
        output_path, zip_path = main()
        print_status(f"\n🎯 Success! All API examples saved and archived.", Fore.GREEN)
        print_status(f"📧 You can now share: {zip_path}", Fore.WHITE)
    except KeyboardInterrupt:
        print_status(f"\n⚠️  Collection interrupted by user", Fore.YELLOW)
    except Exception as e:
        print_status(f"\n💥 Unexpected error: {e}", Fore.RED)
        import traceback
        traceback.print_exc()