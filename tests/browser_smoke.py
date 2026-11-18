"""Exercise the application at a project subpath in Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "example-tool")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=temporary))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH"))
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.route("https://www.polarview.aq/**", lambda route: route.abort())
                page.goto(f"http://127.0.0.1:{server.server_port}/example-tool/")
                page.locator("#first").select_option("2025")
                page.locator("#second").select_option("2024")
                assert "2026-02-16" in page.locator("#chart-first").inner_text()
                assert "2025-02-17" in page.locator("#chart-second").inner_text()
                assert page.locator("#chart-first a").get_attribute("href").endswith(".pdf")
                page.locator("#next").click()
                assert "Week 13" in page.locator("#week-label").inner_text()
                page.locator("#play").click()
                assert page.locator("#play").inner_text() == "Pause"
                page.locator("#play").click()
                page.locator("#second").select_option("2023")
                page.locator("#week").focus()
                page.keyboard.press("Home")
                assert "No chart indexed" in page.locator("#chart-second").inner_text()
                assert page.locator("#prev").is_disabled()
                page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
                assert not errors, errors
                browser.close()
            print("Browser checks passed: project subpath, data interaction and mobile layout")
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
