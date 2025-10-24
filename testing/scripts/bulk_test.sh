#!/bin/bash

# Bulk URL Test Script (Bash/PowerShell compatible)
# =================================================
# 
# This script demonstrates bulk testing using curl commands.
# You can run this in Git Bash, WSL, or adapt the commands for PowerShell.

echo "🚀 Bulk URL Analysis Test"
echo "========================="

# API endpoint
API_URL="http://127.0.0.1:8000/api/v1/analyze"

# Test URLs array
declare -a TEST_URLS=(
    "https://www.legorafi.fr/"
    "https://www.leparisien.fr/sports/"
    "https://www.lemonde.fr/pixels/"
    "https://www.doctissimo.fr/"
    "https://www.routard.com/"
)

# Test descriptions
declare -a DESCRIPTIONS=(
    "Le Gorafi - French Satirical News"
    "Le Parisien - Sports"
    "Le Monde - Technology"
    "Doctissimo - Health"
    "Routard - Travel"
)

# Create results directory
mkdir -p test_results
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="test_results/bulk_test_$TIMESTAMP"
mkdir -p "$RESULTS_DIR"

echo "📁 Results will be saved to: $RESULTS_DIR"
echo ""

# Function to analyze single URL
analyze_url() {
    local url="$1"
    local description="$2"
    local index="$3"
    
    echo "📊 [$index/${#TEST_URLS[@]}] Testing: $description"
    echo "🔗 URL: $url"
    
    # Create JSON payload
    local payload=$(cat <<EOF
{
  "url": "$url",
  "options": {
    "include_sentiment": true,
    "include_entities": true,
    "include_summary": true,
    "include_category": true,
    "include_keywords": true
  }
}
EOF
)
    
    # Make the request and save response
    local response_file="$RESULTS_DIR/response_$index.json"
    local start_time=$(date +%s.%N)
    
    curl -s -X POST "$API_URL" \
         -H "Content-Type: application/json" \
         -d "$payload" \
         -o "$response_file" \
         -w "HTTP Status: %{http_code}\nTime: %{time_total}s\n"
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    
    # Parse and display key results
    if [ -f "$response_file" ]; then
        local category=$(jq -r '.primary_category // "unknown"' "$response_file" 2>/dev/null)
        local sentiment=$(jq -r '.sentiment.overall // "unknown"' "$response_file" 2>/dev/null)
        local confidence=$(jq -r '.category_confidence // 0' "$response_file" 2>/dev/null)
        local status=$(jq -r '.status // "unknown"' "$response_file" 2>/dev/null)
        
        echo "   ✅ Category: $category"
        echo "   😊 Sentiment: $sentiment"
        echo "   📈 Confidence: $confidence"
        echo "   📋 Status: $status"
        echo "   ⏱️  Duration: ${duration}s"
    else
        echo "   ❌ Failed to get response"
    fi
    
    echo ""
}

# Run tests
echo "🎯 Starting bulk analysis..."
echo ""

for i in "${!TEST_URLS[@]}"; do
    analyze_url "${TEST_URLS[$i]}" "${DESCRIPTIONS[$i]}" "$((i+1))"
done

# Generate summary
echo "📋 Generating summary..."

SUMMARY_FILE="$RESULTS_DIR/summary.json"
SUCCESS_COUNT=0
TOTAL_COUNT=${#TEST_URLS[@]}

# Create summary JSON
echo "{" > "$SUMMARY_FILE"
echo "  \"test_info\": {" >> "$SUMMARY_FILE"
echo "    \"timestamp\": \"$(date -Iseconds)\"," >> "$SUMMARY_FILE"
echo "    \"total_urls\": $TOTAL_COUNT," >> "$SUMMARY_FILE"
echo "    \"api_endpoint\": \"$API_URL\"" >> "$SUMMARY_FILE"
echo "  }," >> "$SUMMARY_FILE"
echo "  \"results\": [" >> "$SUMMARY_FILE"

# Combine all results
for i in $(seq 1 $TOTAL_COUNT); do
    response_file="$RESULTS_DIR/response_$i.json"
    if [ -f "$response_file" ] && [ -s "$response_file" ]; then
        # Add test metadata to each result
        temp_file=$(mktemp)
        jq --arg url "${TEST_URLS[$((i-1))]}" --arg desc "${DESCRIPTIONS[$((i-1))]}" \
           '. + {test_url: $url, test_description: $desc}' "$response_file" > "$temp_file"
        
        cat "$temp_file" >> "$SUMMARY_FILE"
        rm "$temp_file"
        
        # Check if successful
        status=$(jq -r '.status // "unknown"' "$response_file" 2>/dev/null)
        if [ "$status" = "success" ]; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        fi
    else
        echo "    {\"test_url\": \"${TEST_URLS[$((i-1))]}\", \"error\": \"No response\"}" >> "$SUMMARY_FILE"
    fi
    
    if [ $i -lt $TOTAL_COUNT ]; then
        echo "," >> "$SUMMARY_FILE"
    fi
done

echo "  ]" >> "$SUMMARY_FILE"
echo "}" >> "$SUMMARY_FILE"

# Display final summary
echo "=" × 60
echo "📊 BULK TEST COMPLETED"
echo "=" × 60
echo "📈 Total URLs: $TOTAL_COUNT"
echo "✅ Successful: $SUCCESS_COUNT"
echo "❌ Failed: $((TOTAL_COUNT - SUCCESS_COUNT))"
echo "📊 Success Rate: $(echo "scale=1; $SUCCESS_COUNT * 100 / $TOTAL_COUNT" | bc -l)%"
echo ""
echo "📁 Results saved in: $RESULTS_DIR"
echo "📋 Summary file: $SUMMARY_FILE"
echo ""
echo "🎉 Test completed!"