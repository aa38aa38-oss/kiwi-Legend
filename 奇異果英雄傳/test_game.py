import os
import time
from playwright.sync_api import sync_playwright

html_path = os.path.abspath("index.html")

with sync_playwright() as p:
    # 使用真正的 WebKit (Safari核心) 模擬 iPhone 14
    iphone = p.devices['iPhone 14']
    browser = p.webkit.launch(headless=False)
    context = browser.new_context(**iphone, has_touch=True)
    page = context.new_page()

    logs = []
    page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda exc: logs.append(f"[ERROR] {exc}"))

    # 打開遊戲
    page.goto(f"file://{html_path}")
    page.wait_for_timeout(1000)

    # 模擬直接觸發進場對話（模擬真實點擊流程）
    page.evaluate("openClubDialogue()")
    page.wait_for_timeout(500)

    # 用真實手指點擊選項
    opt_btn = page.locator(".btn-opt1")
    opt_btn.tap()
    page.wait_for_timeout(1000)

    # 模擬手指按住掌機「▶」按鈕 2 秒
    right_btn = page.locator("#btn-right")
    right_btn.dispatch_event("pointerdown")
    page.wait_for_timeout(2000)
    right_btn.dispatch_event("pointerup")

    # 截圖確認角色是否真的站在夜店地板上並正常右移
    page.screenshot(path="real_iphone_debug.png")

    runtime_info = page.evaluate("""() => {
        return {
            currentScene: currentScene,
            isDialogueOpen: isDialogueOpen,
            playerX: player.x,
            playerY: player.y,
            playerGrounded: player.grounded,
            cameraX: cameraX,
            dialogDisplay: document.getElementById('dialog-box').style.display
        };
    }""")

    with open("real_iphone_log.txt", "w", encoding="utf-8") as f:
        f.write("=== iPhone 運行日誌 ===\n")
        f.write("\n".join(logs) + "\n\n")
        f.write("=== 內部變數狀態 ===\n")
        for k, v in runtime_info.items():
            f.write(f"{k}: {v}\n")

    browser.close()
    print("iPhone 真機模擬測試完成！已產出 real_iphone_debug.png 與 real_iphone_log.txt")
