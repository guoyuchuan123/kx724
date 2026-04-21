@echo off
chcp 65001 >nul
title 同花顺7*24快讯抓取工具

echo ========================================
echo    同花顺7*24快讯抓取工具
echo ========================================
echo.

:menu
echo 请选择运行模式：
echo.
echo 1. 默认模式（获取当天数据，每5分钟定时抓取）
echo 2. 指定日期模式（获取指定日期的数据）
echo 3. 政策利好股票分析模式
echo 4. 新闻分析模式
echo 5. 基本面数据获取模式（获取沪市主板、深市主板、创业板基本面数据）
echo 6. 退出
echo.

set /p choice=请输入选项 (1-6): 

if "%choice%"=="1" goto default_mode
if "%choice%"=="2" goto date_mode
if "%choice%"=="3" goto policy_mode
if "%choice%"=="4" goto news_mode
if "%choice%"=="5" goto fundamental_mode
if "%choice%"=="6" goto end
echo.
echo 无效的选项，请重新选择
echo.
goto menu

:default_mode
echo.
echo 启动默认模式...
echo.
python news_scraper.py
pause
goto menu

:date_mode
echo.
set /p date=请输入日期 (格式: YYYY-MM-DD，例如 2026-04-17): 
echo.
echo 启动指定日期模式: %date%
echo.
python news_scraper.py %date%
pause
goto menu

:policy_mode
echo.
set /p policy=请输入政策文本: 
echo.
echo 启动政策利好股票分析模式...
echo.
python news_scraper.py --policy "%policy%"
pause
goto menu

:news_mode
echo.
set /p title=请输入新闻标题: 
set /p content=请输入新闻内容: 
echo.
echo 启动新闻分析模式...
echo.
python news_scraper.py --analyze "%title%" "%content%"
pause
goto menu

:fundamental_mode
echo.
echo 启动基本面数据获取模式...
echo.
python fetch_fundamental_data.py
pause
goto menu

:end
echo.
echo 感谢使用，再见！
exit
