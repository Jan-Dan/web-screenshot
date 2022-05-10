#!/bin/python3
# WebSH.py - create a screenshot of a given URL webpage
# Written by Jan-Dan 09. Mai 2022
# EXAMPLE CALL:
# import websh
# screener = websh.WebSH()
# screener.set_outfile(filename)
# screener.set_url(parameter)
# await screener.take_screenshot()

import time
import asyncio
import pyppeteer


class WebSH:

    def __init__(self, url='https://www.google.com', outfile='file.png', auth_string='', width_px=1280):
        self.url = url
        self.auth_string = auth_string
        self.outfile = outfile
        self.width_px = width_px

    async def take_screenshot(self):
        browser = await pyppeteer.launch({'headless': True, 'defaultViewport': False})
        page = await browser.newPage()
        if self.auth_string != '':
            # Generate authorization header for basic auth
            auth_header = 'Bearer ' + self.auth_string
            # Set basic auth headers
            await page.setExtraHTTPHeaders({'Authorization': auth_header})
        # Increase timeout from the default of 30 seconds to 120 seconds, to allow for slow-loading panels
        page.setDefaultNavigationTimeout(120000)
        # Wait until all network connections are closed (and none are opened withing 0.5s).
        # In some cases it may be appropriate to change this to {waitUntil: 'networkidle2'},
        # which stops when there are only 2 or fewer connections remaining.
        await page.goto(self.url, {'waitUntil': 'networkidle0'})
        # Get the height of the main canvas, and add a margin
        # If this goes to grafana (local raspberrypi server) we need to get the height in a different way
        if self.url.startswith("http://raspberrypi:3000/d/"):
            height_array = await page.evaluate('''() => {
                return {
                    height: document.getElementsByClassName('react-grid-layout')[0].getBoundingClientRect().bottom
                }
            }''')
        else:
            height_array = await page.evaluate('''() => {
                return {
                    height: document.documentElement.scrollHeight
                }
            }''')
        # add a margin
        height_px = min(1500, (height_array['height'] + 20))
        # Increasing the deviceScaleFactor gets a higher-resolution image. And set the height and width
        await page.setViewport({
            'width': self.width_px,
            'height': height_px,
            'deviceScaleFactor': 2,
            'isMobile': False
        })
        # Click away the cookie banner :angry: Add more words to the regex
        await page.evaluate('''() => {
            function xcc_contains(selector, text)
            {
                var elements = document.querySelectorAll(selector);
                return Array.prototype.filter.call(elements, function(element)
                    {
                        return RegExp(text, "i").test(element.textContent.trim());
                    }
                );
            }
            var _xcc;
            _xcc = xcc_contains('[id*=cookie] a, [class*=cookie] a, [id*=cookie] button, [class*=cookie] button, [class*=button] a', '^(Alle akzeptieren|Alles akzeptieren|Akzeptieren|Verstanden|Zustimmen|Okay|OK|I AGREE|ICH AKZEPTIERE|Accept all cookies)$');
            //var xpath = "//a[text()='Accept all cookies']";
            //_xcc = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (_xcc != null && _xcc.length != 0) 
            {
                _xcc[0].click();
            }
        }''')
        time.sleep(1)  # Waiting for all graphs/images to load
        await page.screenshot({'path': self.outfile, 'width': self.width_px, 'height': height_px})
        await browser.close()

    # If page displays a js.alert on first load -> try closing it
    async def close_dialog(self, dialog):
        print(dialog.message)
        await dialog.dismiss()

    # Private URL
    def set_monitoring(self):
        self.url = "http://raspberrypi:3000/d/yWbfoTEnz/monitoring-pi?kiosk&orgId=1"

    # Private URL
    def set_sensors(self):
        self.url = "http://raspberrypi:3000/d/zMXDeRsnz/sensoren?kiosk&orgId=1"

    # Private URL
    def set_gasstations(self):
        self.url = "http://raspberrypi:3000/d/yUhc7Gs7z/tankstellen?kiosk&orgId=1"

    def set_url(self, url):
        self.url = url

    def set_auth_string(self, auth_string):
        self.auth_string = auth_string

    def set_outfile(self, outfile):
        self.outfile = outfile

    def set_width(self, width):
        self.width_px = width

    def get_outfile(self):
        return self.outfile

    def get_url(self):
        return self.url


# This script an easily be used as an import class. But you may use it directly
if __name__ == "__main__":
    url = input("What URL to Screenshot> ")
    auth_string = input("Authentication (leave empty for none)> ")
    outfile = 'output.png'
    screener = WebSH(url, outfile, auth_string)
    asyncio.get_event_loop().run_until_complete(screener.take_screenshot())
