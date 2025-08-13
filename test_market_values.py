#!/usr/bin/env python3
"""
Test market value parsing
"""

import re

def parse_market_value(value_text: str) -> float:
    """Parse market value text and return value in millions EUR
    
    Examples:
    - "25.00m" -> 25.0
    - "120.5m" -> 120.5
    - "500k" -> 0.5
    - "1.2bn" -> 1200.0
    """
    if not value_text or value_text.strip() in ['-', '?', 'N/A', '', '--']:
        return 1.0  # Default minimum value
    
    # Clean the text - remove €, currency symbols, spaces
    value_text = value_text.strip().lower()
    value_text = re.sub(r'[€$£¥₹]', '', value_text)  # Remove currency symbols
    value_text = value_text.replace(',', '').replace(' ', '')
    
    # Extract number and suffix using regex
    # Match patterns like: 25.00m, 120m, 500k, 1.2bn, etc.
    pattern = r'(\d+(?:\.\d+)?)\s*([kmbt])?(?:il|illion|n)?'
    match = re.search(pattern, value_text)
    
    if not match:
        # Try to extract just a number if no pattern matches
        number_match = re.search(r'(\d+(?:\.\d+)?)', value_text)
        if number_match:
            number = float(number_match.group(1))
            # If it's a large number without suffix, assume it's in full currency
            if number > 1000000:
                return number / 1000000  # Convert to millions
            else:
                return max(number, 1.0)
        return 1.0
    
    number = float(match.group(1))
    suffix = match.group(2)
    
    if suffix == 'k':
        return number / 1000  # Convert thousands to millions (e.g., 500k = 0.5m)
    elif suffix == 'm':
        return number  # Already in millions (e.g., 25.00m = 25.0)
    elif suffix in ['b', 't']:
        return number * 1000  # Convert billions to millions (e.g., 1.2b = 1200m)
    else:
        # No suffix - assume it's already the right unit or needs conversion
        if number > 1000:
            return number / 1000  # Large numbers are probably in thousands
        else:
            return max(number, 0.1)  # Small numbers are probably already in millions

def test_parsing():
    """Test various market value formats"""
    test_cases = [
        "25.00m",       # Should be 25.0
        "€120.5m",      # Should be 120.5
        "500k",         # Should be 0.5
        "€1.2bn",       # Should be 1200.0
        "75.0m",        # Should be 75.0
        "2.5m",         # Should be 2.5
        "800k",         # Should be 0.8
        "1.5bn",        # Should be 1500.0
        "€25.00m",      # Should be 25.0
        "45m",          # Should be 45.0
        "-",            # Should be 1.0 (default)
        "N/A",          # Should be 1.0 (default)
        "€200k",        # Should be 0.2
        "3.7m",         # Should be 3.7
    ]
    
    print("🧪 TESTING MARKET VALUE PARSING")
    print("=" * 50)
    
    for test_input in test_cases:
        result = parse_market_value(test_input)
        print(f"'{test_input:10s}' -> {result:6.1f}M")
    
    print("\n✅ Test completed!")
    print("\nExpected results:")
    print("- Values ending in 'm' should keep the number as-is")
    print("- Values ending in 'k' should be divided by 1000") 
    print("- Values ending in 'bn' should be multiplied by 1000")
    print("- Invalid values should default to 1.0")

if __name__ == "__main__":
    test_parsing()
