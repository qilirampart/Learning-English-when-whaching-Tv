# Railway API 测试脚本
# 使用方法: .\test_railway_api.ps1 "你的Railway域名"

param(
    [Parameter(Mandatory=$true)]
    [string]$Domain
)

$baseUrl = "https://$Domain"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Railway 后端 API 测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "测试域名: $baseUrl" -ForegroundColor Yellow
Write-Host ""

# 测试 1: 统计概览
Write-Host "【测试 1】获取统计概览..." -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/statistics/overview" -Method Get
    Write-Host "✅ 成功！" -ForegroundColor Green
    Write-Host "数据:" -ForegroundColor White
    $response | ConvertTo-Json -Depth 3
    Write-Host ""
} catch {
    Write-Host "❌ 失败: $_" -ForegroundColor Red
    Write-Host ""
}

# 测试 2: 查询单词
Write-Host "【测试 2】查询单词 'hello'..." -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/words/query?word=hello" -Method Get
    Write-Host "✅ 成功！" -ForegroundColor Green
    Write-Host "数据:" -ForegroundColor White
    $response | ConvertTo-Json -Depth 3
    Write-Host ""
} catch {
    Write-Host "❌ 失败: $_" -ForegroundColor Red
    Write-Host ""
}

# 测试 3: 获取单词列表
Write-Host "【测试 3】获取单词列表..." -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/words?page=1&per_page=10" -Method Get
    Write-Host "✅ 成功！" -ForegroundColor Green
    Write-Host "数据:" -ForegroundColor White
    $response | ConvertTo-Json -Depth 3
    Write-Host ""
} catch {
    Write-Host "❌ 失败: $_" -ForegroundColor Red
    Write-Host ""
}

# 测试 4: 获取学习计划
Write-Host "【测试 4】获取今日学习计划..." -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/learning/plan/today" -Method Get
    Write-Host "✅ 成功！" -ForegroundColor Green
    Write-Host "数据:" -ForegroundColor White
    $response | ConvertTo-Json -Depth 3
    Write-Host ""
} catch {
    Write-Host "❌ 失败: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

