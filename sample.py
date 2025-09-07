"""
Enhanced endpoints Test Script
This file demonstrates all available endpoints with improved formatting and extended response display.

Base URL: http://localhost:8005
API Documentation: http://localhost:8005/docs

Available property_ids: 1, 6
Available scrap_types: A (hourly), B (daily)
AI Models: baseline, optimized_baseline
"""

import requests
import pandas as pd
import json
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8005"
API_PREFIX = "/smart_pricing_api/v2"
PROPERTY_IDS = [1, 6]
SCRAP_TYPES = ["A", "B"]
DEFAULT_TIMEZONE = "Asia/Seoul"

current_time = pd.Timestamp.now(tz=DEFAULT_TIMEZONE)
SAMPLE_DATE = current_time.isoformat()

AI_MODELS = ["baseline", "optimized_baseline"]

def print_header(title, color=Fore.CYAN):
    """Print a beautifully formatted header"""
    width = 100
    print(f"\n{color}{'=' * width}{Style.RESET_ALL}")
    print(f"{color}{title.center(width)}{Style.RESET_ALL}")
    print(f"{color}{'=' * width}{Style.RESET_ALL}")

def print_endpoint_info(title, method, url, description):
    """Enhanced function to print endpoint information with better formatting"""
    print(f"\n{Fore.YELLOW}{'─' * 100}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📍 {title}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 100}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}🔹 Method:{Style.RESET_ALL} {Fore.WHITE}{method}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}🔹 URL:{Style.RESET_ALL} {Fore.WHITE}{url}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}🔹 Description:{Style.RESET_ALL} {description}")
    print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")

def format_json_pretty(data, max_chars=2500):
    """Format JSON data with proper indentation and color"""
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        
        if len(formatted) > max_chars:
            truncated = formatted[:max_chars]
            last_newline = truncated.rfind('\n')
            if last_newline > max_chars - 200:  # If close to the end, use it
                truncated = truncated[:last_newline]
            
            return (
                f"{Fore.WHITE}{truncated}{Style.RESET_ALL}\n"
                f"{Fore.YELLOW}... [Response truncated - showing first {len(truncated)} characters of {len(formatted)} total]{Style.RESET_ALL}"
            )
        else:
            return f"{Fore.WHITE}{formatted}{Style.RESET_ALL}"
    except Exception as e:
        return f"{Fore.RED}Error formatting JSON: {e}{Style.RESET_ALL}\n{data}"

def make_request(method, url, payload=None, params=None, description="", max_response_length=5000):
    """Enhanced function to make requests and display results with better formatting"""
    try:
        print(f"{Fore.MAGENTA}🚀 Making {method} request...{Style.RESET_ALL}")
        
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=payload, timeout=10)
        else:
            print(f"{Fore.RED}❌ Unsupported method: {method}{Style.RESET_ALL}")
            return
            
        # Status code with color coding
        if response.status_code == 200:
            status_color = Fore.GREEN
            status_icon = "✅"
        elif response.status_code in [400, 401, 403, 404]:
            status_color = Fore.YELLOW
            status_icon = "⚠️"
        else:
            status_color = Fore.RED
            status_icon = "❌"
            
        print(f"{status_color}{status_icon} Status Code: {response.status_code}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔗 Final URL: {response.url}{Style.RESET_ALL}")
        
        if params:
            print(f"{Fore.BLUE}📋 Parameters: {params}{Style.RESET_ALL}")
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}📦 Response Structure:{Style.RESET_ALL}")
            try:
                response_json = response.json()
                formatted_response = format_json_pretty(response_json, max_response_length)
                print(formatted_response)
                
                if isinstance(response_json, dict):
                    keys = list(response_json.keys())
                    print(f"{Fore.CYAN}🔑 Response Keys: {keys}{Style.RESET_ALL}")
                elif isinstance(response_json, list):
                    print(f"{Fore.CYAN}📊 Response Type: List with {len(response_json)} items{Style.RESET_ALL}")
                    
            except json.JSONDecodeError:
                print(f"{Fore.YELLOW}⚠️  Response is not JSON format{Style.RESET_ALL}")
                content = response.text[:max_response_length]
                if len(response.text) > max_response_length:
                    content += f"... [truncated from {len(response.text)} chars]"
                print(content)
        else:
            print(f"{Fore.RED}💥 Error Response:{Style.RESET_ALL}")
            print(f"{Fore.RED}{response.text[:1000]}{Style.RESET_ALL}")
            try:
                error_json = response.json()
                print(f"{Fore.RED}📋 Error Details:{Style.RESET_ALL}")
                print(format_json_pretty(error_json, 1000))
            except:
                pass
                
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}🔌 Connection Error: Could not connect to {url}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Make sure the API server is running on {BASE_URL}{Style.RESET_ALL}")
    except requests.exceptions.Timeout:
        print(f"{Fore.RED}⏰ Timeout Error: Request took longer than 10 seconds{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}💥 Request failed: {e}{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}{'─' * 100}{Style.RESET_ALL}\n")

def test_connection():
    """Test basic connection to the API server"""
    print_header("🔍 CONNECTION TEST", Fore.MAGENTA)
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print(f"{Fore.GREEN}✅ Server is running and accessible{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  Server responded with status: {response.status_code}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Cannot connect to server: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Make sure the API server is running on {BASE_URL}{Style.RESET_ALL}")
        return False

def main():
    """Main function to run all API tests"""
    print_header("🚀 SMART PRICING API v2 - ENHANCED TEST SUITE", Fore.CYAN)
    print(f"{Fore.WHITE}Base URL: {BASE_URL}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}API Prefix: {API_PREFIX}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Sample Date: {SAMPLE_DATE}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Properties: {PROPERTY_IDS}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Scrap Types: {SCRAP_TYPES} (A=hourly, B=daily){Style.RESET_ALL}")
    
    if not test_connection():
        print(f"{Fore.RED}⚠️  Continuing with tests despite connection issues...{Style.RESET_ALL}")
    
    # =============================================================================
    # DEBUGGING - CHECK AVAILABLE ROUTES
    # =============================================================================
    
    print_header("🛠️  DEBUGGING & DISCOVERY", Fore.MAGENTA)
    
    print_endpoint_info(
        "OpenAPI Schema", 
        "GET", 
        f"{BASE_URL}/openapi.json",
        "Get OpenAPI schema to see all registered endpoints"
    )
    make_request("GET", f"{BASE_URL}/openapi.json")
    
    # =============================================================================
    # ROOT ENDPOINT
    # =============================================================================
    
    print_header("🏠 ROOT ENDPOINTS", Fore.BLUE)
    
    print_endpoint_info(
        "API Root", 
        "GET", 
        f"{BASE_URL}/",
        "Get API root information and version"
    )
    make_request("GET", f"{BASE_URL}/")
    
    # =============================================================================
    # HEALTH CHECK ENDPOINTS
    # =============================================================================
    
    print_header("🏥 HEALTH CHECK ENDPOINTS", Fore.GREEN)
    
    print_endpoint_info(
        "Comprehensive Health Check", 
        "GET", 
        f"{BASE_URL}{API_PREFIX}/health/",
        "Get comprehensive health status including system metrics and path checks"
    )
    make_request("GET", f"{BASE_URL}{API_PREFIX}/health/")
    
    print_endpoint_info(
        "Readiness Check", 
        "GET", 
        f"{BASE_URL}{API_PREFIX}/health/ready",
        "Simple readiness check for load balancers"
    )
    make_request("GET", f"{BASE_URL}{API_PREFIX}/health/ready")
    
    print_endpoint_info(
        "Liveness Check", 
        "GET", 
        f"{BASE_URL}{API_PREFIX}/health/live",
        "Simple liveness check for Kubernetes"
    )
    make_request("GET", f"{BASE_URL}{API_PREFIX}/health/live")
    
    # =============================================================================
    # UPDATE STATUS ENDPOINTS
    # =============================================================================
    
    print_header("📊 UPDATE STATUS ENDPOINTS", Fore.CYAN)
    
    for scrap_type in SCRAP_TYPES:
        type_desc = "hourly" if scrap_type == "A" else "daily"
        print_endpoint_info(
            f"Latest Updates - Type {scrap_type} ({type_desc})", 
            "GET", 
            f"{BASE_URL}{API_PREFIX}/updates/latest/{scrap_type}",
            f"Get latest update timestamps for scrap type {scrap_type}"
        )
        make_request("GET", f"{BASE_URL}{API_PREFIX}/updates/latest/{scrap_type}")
    
    print_endpoint_info(
        "Overall Update Status", 
        "GET", 
        f"{BASE_URL}{API_PREFIX}/updates/status",
        "Get overall update status for both scrap types A and B"
    )
    make_request("GET", f"{BASE_URL}{API_PREFIX}/updates/status")
    
    # =============================================================================
    # DATA ENDPOINTS
    # =============================================================================
    
    print_header("💾 DATA ENDPOINTS", Fore.YELLOW)
    
    print_endpoint_info(
        "Properties Configuration", 
        "GET", 
        f"{BASE_URL}{API_PREFIX}/data/properties",
        "Get all available properties with their configurations"
    )
    make_request("GET", f"{BASE_URL}{API_PREFIX}/data/properties")
    
    print_header("💰 COMPETITOR PRICES", Fore.RED)
    for property_id in PROPERTY_IDS:
        for scrap_type in SCRAP_TYPES:
            type_desc = "hourly" if scrap_type == "A" else "daily"
            print_endpoint_info(
                f"Competitor Prices - Property {property_id}, Type {scrap_type} ({type_desc})", 
                "GET", 
                f"{BASE_URL}{API_PREFIX}/data/comp-prices/{property_id}",
                f"Get competitor prices for property {property_id} on {SAMPLE_DATE}"
            )
            params = {
                "date": SAMPLE_DATE,
                "scrap_type": scrap_type
            }
            make_request("GET", f"{BASE_URL}{API_PREFIX}/data/comp-prices/{property_id}", params=params)
    
    print_header("🤖 AI PRICE PREDICTIONS", Fore.MAGENTA)
    for property_id in PROPERTY_IDS:
        for scrap_type in SCRAP_TYPES:
            for model in AI_MODELS:
                type_desc = "hourly" if scrap_type == "A" else "daily"
                print_endpoint_info(
                    f"AI Prices - Property {property_id}, Type {scrap_type} ({type_desc}), Model {model}", 
                    "GET", 
                    f"{BASE_URL}{API_PREFIX}/data/ai-prices/{property_id}",
                    f"Get AI price predictions using {model} model"
                )
                params = {
                    "date": SAMPLE_DATE,
                    "model": model,
                    "scrap_type": scrap_type
                }
                make_request("GET", f"{BASE_URL}{API_PREFIX}/data/ai-prices/{property_id}", params=params)
    
    print_header("📈 MARKET STATISTICS", Fore.BLUE)
    for property_id in PROPERTY_IDS:
        print_endpoint_info(
            f"Market Statistics - Property {property_id}", 
            "GET", 
            f"{BASE_URL}{API_PREFIX}/data/market-stats/{property_id}",
            f"Get market statistics for property {property_id} on {SAMPLE_DATE}"
        )
        params = {"date": SAMPLE_DATE}
        make_request("GET", f"{BASE_URL}{API_PREFIX}/data/market-stats/{property_id}", params=params)
    
    print_header("🎭 EVENTS DATA", Fore.GREEN)
    for property_id in PROPERTY_IDS:
        print_endpoint_info(
            f"Events - Property {property_id}", 
            "GET", 
            f"{BASE_URL}{API_PREFIX}/data/events/{property_id}",
            f"Get events data for property {property_id} on {SAMPLE_DATE}"
        )
        params = {"date": SAMPLE_DATE}
        make_request("GET", f"{BASE_URL}{API_PREFIX}/data/events/{property_id}", params=params)
    
    print_header("✅ TEST SUITE COMPLETE", Fore.GREEN)
    print(f"{Fore.CYAN}📋 Summary:{Style.RESET_ALL}")
    print(f"  • All endpoints have been tested")
    print(f"  • Response content limited to 5000 characters per response")
    print(f"  • Check the results above for any errors or issues")
    print(f"  • API Documentation: {BASE_URL}/docs")
    print(f"{Fore.YELLOW}💡 Tip: Install colorama for better formatting: pip install colorama{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Test suite interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}💥 Unexpected error: {e}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}🎯 Done! Check the output above for API responses.{Style.RESET_ALL}")