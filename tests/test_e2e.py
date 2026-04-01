import os
import pytest
import uuid
from playwright.sync_api import Page, expect

def test_login_and_dashboard_visibility(logged_in_page: Page):
    """Verifies dashboard title and basic visibility."""
    expect(logged_in_page.get_by_text("Parents Bank").first).to_be_visible()
    expect(logged_in_page).to_have_title("Parents Bank - Dashboard")
    expect(logged_in_page.get_by_text("Total Family Vault")).to_be_visible()

def test_positive_transaction_flow(logged_in_page: Page):
    """
    Business Scenario: Add a positive transaction and verify balance update.
    """
    unique_desc = f"Grandma gift {uuid.uuid4().hex[:6]}"
    amount = "50.00"
    
    # Open Deposit modal
    logged_in_page.get_by_role("button", name="Deposit").first.click()
    
    # Fill form
    logged_in_page.get_by_placeholder("0.00").fill(amount)
    logged_in_page.get_by_placeholder("E.g., Allowance, Chores...").fill(unique_desc)
    
    # Submit
    logged_in_page.get_by_role("button", name="Deposit Funds").click()
    
    # Verify balance on dashboard
    # Child 1 starts with 0.00, should now have 50.00
    expect(logged_in_page.get_by_text("50.00 zł").first).to_be_visible()
    # Verify recent activity
    expect(logged_in_page.get_by_text(unique_desc)).to_be_visible()

def test_negative_transaction_flow(logged_in_page: Page):
    """
    Business Scenario: Add a negative transaction (expense) and verify balance decrease.
    """
    unique_desc = f"Toy car {uuid.uuid4().hex[:6]}"
    amount = "15.50"
    
    # Open Withdraw modal
    logged_in_page.get_by_role("button", name="Withdraw").first.click()
    
    # Fill form
    logged_in_page.get_by_placeholder("0.00").fill(amount)
    logged_in_page.get_by_placeholder("E.g., Allowance, Chores...").fill(unique_desc)
    
    # Submit
    logged_in_page.get_by_role("button", name="Withdraw Funds").click()
    
    # Verify balance on dashboard (0 - 15.50 = -15.50)
    expect(logged_in_page.get_by_text("-15.50 zł").first).to_be_visible()
    # Verify recent activity
    expect(logged_in_page.get_by_text(unique_desc)).to_be_visible()

def test_child_profile_name_update(logged_in_page: Page):
    """
    Business Scenario: Change child name in settings and verify on dashboard.
    """
    new_name = f"Hero {uuid.uuid4().hex[:4]}"
    
    # Open settings
    logged_in_page.get_by_role("button").filter(has=logged_in_page.locator("svg path[d*='M10.325']")).click()
    
    # Change name of Slot 1 (Child 1)
    logged_in_page.locator("#setting-name-1").fill(new_name)
    
    # Save
    logged_in_page.get_by_role("button", name="Save Changes").click()
    
    # Verify new name on dashboard
    expect(logged_in_page.get_by_role("heading", name=new_name)).to_be_visible()
    # Verify Slot 1 name in dashboard cards
    expect(logged_in_page.get_by_text(new_name)).to_be_visible()

def test_data_persistence_after_refresh(logged_in_page: Page):
    """
    Business Scenario: Transaction persists after page refresh.
    """
    unique_desc = f"Savings {uuid.uuid4().hex[:6]}"
    amount = "100"
    
    # Add transaction
    logged_in_page.get_by_role("button", name="Deposit").first.click()
    logged_in_page.get_by_placeholder("0.00").fill(amount)
    logged_in_page.get_by_placeholder("E.g., Allowance, Chores...").fill(unique_desc)
    logged_in_page.get_by_role("button", name="Deposit Funds").click()
    
    # Verify visible
    expect(logged_in_page.get_by_text("100.00 zł").first).to_be_visible()
    expect(logged_in_page.get_by_text(unique_desc)).to_be_visible()
    
    # REFRESH
    logged_in_page.reload()
    
    # Verify still visible
    expect(logged_in_page.get_by_text("100.00 zł").first).to_be_visible()
    expect(logged_in_page.get_by_text(unique_desc)).to_be_visible()
