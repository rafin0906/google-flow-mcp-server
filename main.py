"""
Main Entry Point for Google Flow Automation
"""

from app.automation.flow import run_flow

if __name__ == "__main__":
    run_flow(headless=False)
