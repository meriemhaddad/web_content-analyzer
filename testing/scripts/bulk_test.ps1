# Bulk URL Test Script (PowerShell)
# ================================
# 
# PowerShell script for bulk testing the Web Content Analysis Agent

Write-Host "🚀 Bulk URL Analysis Test" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Configuration
$ApiUrl = "http://127.0.0.1:8000/api/v1/analyze"
$MaxConcurrent = 3

# Test URLs with expected categories
$TestUrls = @(
    @{
        Url = "https://www.legorafi.fr/"
        Description = "Le Gorafi - French Satirical News"
        Expected = "satire"
    },
    @{
        Url = "https://www.leparisien.fr/sports/"
        Description = "Le Parisien - Sports Section"
        Expected = "sports"
    },
    @{
        Url = "https://www.lemonde.fr/pixels/"
        Description = "Le Monde - Technology News"
        Expected = "technology"
    },
    @{
        Url = "https://www.doctissimo.fr/"
        Description = "Doctissimo - Health Information"
        Expected = "health"
    },
    @{
        Url = "https://www.routard.com/"
        Description = "Routard - Travel Guide"
        Expected = "travel"
    },
    @{
        Url = "https://www.marmiton.org/"
        Description = "Marmiton - Cooking Recipes"
        Expected = "lifestyle"
    }
)

# Create results directory
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ResultsDir = "test_results\bulk_test_$Timestamp"
New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null

Write-Host "📁 Results will be saved to: $ResultsDir" -ForegroundColor Cyan
Write-Host ""

# Function to test single URL
function Test-SingleUrl {
    param(
        [hashtable]$UrlData,
        [int]$Index,
        [int]$Total
    )
    
    $Url = $UrlData.Url
    $Description = $UrlData.Description
    $Expected = $UrlData.Expected
    
    Write-Host "📊 [$Index/$Total] Testing: $Description" -ForegroundColor Yellow
    Write-Host "🔗 URL: $Url" -ForegroundColor Gray
    
    # Create request payload
    $Payload = @{
        url = $Url
        options = @{
            include_sentiment = $true
            include_entities = $true
            include_summary = $true
            include_category = $true
            include_keywords = $true
        }
    } | ConvertTo-Json -Depth 3
    
    # Measure request time
    $StartTime = Get-Date
    
    try {
        # Make the API request
        $Response = Invoke-RestMethod -Uri $ApiUrl -Method Post -Body $Payload -ContentType "application/json" -TimeoutSec 30
        $EndTime = Get-Date
        $Duration = ($EndTime - $StartTime).TotalSeconds
        
        # Extract key information
        $Category = $Response.primary_category
        $Sentiment = $Response.sentiment.overall
        $Confidence = $Response.category_confidence
        $Status = $Response.status
        
        # Display results
        $CategoryMatch = if ($Category -eq $Expected) { "✅" } else { "⚠️" }
        Write-Host "   $CategoryMatch Category: $Category (expected: $Expected)" -ForegroundColor $(if ($Category -eq $Expected) { "Green" } else { "Yellow" })
        Write-Host "   😊 Sentiment: $Sentiment" -ForegroundColor Cyan
        Write-Host "   📈 Confidence: $($Confidence.ToString('F2'))" -ForegroundColor Cyan
        Write-Host "   📋 Status: $Status" -ForegroundColor Cyan
        Write-Host "   ⏱️  Duration: $($Duration.ToString('F2'))s" -ForegroundColor Cyan
        
        # Add test metadata
        $Response | Add-Member -NotePropertyName "test_url" -NotePropertyValue $Url
        $Response | Add-Member -NotePropertyName "test_description" -NotePropertyValue $Description
        $Response | Add-Member -NotePropertyName "expected_category" -NotePropertyValue $Expected
        $Response | Add-Member -NotePropertyName "processing_time" -NotePropertyValue $Duration
        $Response | Add-Member -NotePropertyName "category_match" -NotePropertyValue ($Category -eq $Expected)
        
        # Save individual result
        $ResponseFile = "$ResultsDir\response_$Index.json"
        $Response | ConvertTo-Json -Depth 10 | Out-File -FilePath $ResponseFile -Encoding UTF8
        
        return $Response
        
    } catch {
        $EndTime = Get-Date
        $Duration = ($EndTime - $StartTime).TotalSeconds
        
        Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   ⏱️  Duration: $($Duration.ToString('F2'))s" -ForegroundColor Cyan
        
        $ErrorResult = @{
            test_url = $Url
            test_description = $Description
            expected_category = $Expected
            error = $_.Exception.Message
            processing_time = $Duration
            status = "error"
        }
        
        # Save error result
        $ErrorFile = "$ResultsDir\error_$Index.json"
        $ErrorResult | ConvertTo-Json | Out-File -FilePath $ErrorFile -Encoding UTF8
        
        return $ErrorResult
    }
    
    Write-Host ""
}

# Run tests
Write-Host "🎯 Starting bulk analysis of $($TestUrls.Count) URLs..." -ForegroundColor Green
Write-Host ""

$Results = @()
$SuccessCount = 0
$TotalStartTime = Get-Date

for ($i = 0; $i -lt $TestUrls.Count; $i++) {
    $Result = Test-SingleUrl -UrlData $TestUrls[$i] -Index ($i + 1) -Total $TestUrls.Count
    $Results += $Result
    
    if ($Result.status -eq "success") {
        $SuccessCount++
    }
    
    Write-Host ""
}

$TotalEndTime = Get-Date
$TotalDuration = ($TotalEndTime - $TotalStartTime).TotalSeconds

# Generate summary
Write-Host "📋 Generating summary..." -ForegroundColor Yellow

$Summary = @{
    test_info = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        total_urls = $TestUrls.Count
        successful = $SuccessCount
        failed = $TestUrls.Count - $SuccessCount
        success_rate = [math]::Round(($SuccessCount / $TestUrls.Count) * 100, 1)
        total_duration = [math]::Round($TotalDuration, 2)
        average_duration = [math]::Round($TotalDuration / $TestUrls.Count, 2)
        api_endpoint = $ApiUrl
    }
    results = $Results
}

# Save summary
$SummaryFile = "$ResultsDir\summary.json"
$Summary | ConvertTo-Json -Depth 10 | Out-File -FilePath $SummaryFile -Encoding UTF8

# Display final summary
Write-Host "=" × 60 -ForegroundColor Green
Write-Host "📊 BULK TEST COMPLETED" -ForegroundColor Green
Write-Host "=" × 60 -ForegroundColor Green

Write-Host "📈 Total URLs: $($TestUrls.Count)" -ForegroundColor White
Write-Host "✅ Successful: $SuccessCount" -ForegroundColor Green
Write-Host "❌ Failed: $($TestUrls.Count - $SuccessCount)" -ForegroundColor Red
Write-Host "📊 Success Rate: $($Summary.test_info.success_rate)%" -ForegroundColor Cyan
Write-Host "⏱️  Total Time: $($Summary.test_info.total_duration)s" -ForegroundColor Cyan
Write-Host "⚡ Average Time: $($Summary.test_info.average_duration)s per URL" -ForegroundColor Cyan

# Category accuracy
$CategoryMatches = ($Results | Where-Object { $_.category_match -eq $true }).Count
if ($SuccessCount -gt 0) {
    $CategoryAccuracy = [math]::Round(($CategoryMatches / $SuccessCount) * 100, 1)
    Write-Host "🎯 Category Accuracy: $CategoryAccuracy%" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "📁 Results saved in: $ResultsDir" -ForegroundColor Yellow
Write-Host "📋 Summary file: $SummaryFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎉 Test completed!" -ForegroundColor Green

# Optionally open results directory
$OpenResults = Read-Host "Would you like to open the results directory? (y/n)"
if ($OpenResults -eq "y" -or $OpenResults -eq "Y") {
    Invoke-Item $ResultsDir
}