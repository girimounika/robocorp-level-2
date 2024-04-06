from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        headless=False,
        slowmo=100,
    )
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)  
    archive_receipts() 

def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Read data from csv"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    csv = Tables()
    worksheet = csv.read_table_from_csv("orders.csv", header=True)
    return worksheet

def close_annoying_modal():
    """Clicks on ok on dialog box"""
    page = browser.page()  
    page.click("text=OK")

def fill_the_form(order):
    """Fills in the orders data and click the 'Order' button"""
    page = browser.page()
    page.select_option("#head",value=(order['Head']))
    page.check("#id-body-" + str(order['Body']))
    page.fill("css=.form-control", order['Legs'])
    page.fill("#address", order['Address'])
    page.click("text=Preview")
    page.click("#order")
    while not page.locator("#order-another"):
        page.click("#order")
    store_receipt_as_pdf(order['Order number'])
    screenshot_robot(order['Order number'])
    embed_screenshot_to_receipt("output/{order_number}.png","output/{order_number}.pdf")
    page.click("text=Order another robot")

def store_receipt_as_pdf(order_number):
    """Store receipt as PDF"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, "output/{order_number}.pdf")

def screenshot_robot(order_number):
    page = browser.page()
    robot = page.locator("#robot-preview-image")
    robot.screenshot(path="output/{order_number}.png")

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed screenshot with PDF"""
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def archive_receipts():
    """Archive the receipts"""
    folder = Archive()
    folder.archive_folder_with_zip("output", "output/orders.zip", include="*.pdf")
    
    

