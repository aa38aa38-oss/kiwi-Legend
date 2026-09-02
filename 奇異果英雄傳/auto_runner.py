import os
import time
from playwright.sync_api import sync_playwright

html_file = os.path.abspath("index.html")

print("========================================")
print(" 🤖 啟動 iPhone 真機全自動除錯巡檢機器人")
print("========================================")

with sync_playwright() as p:
    iphone = p.devices['iPhone 14']
    browser = p.webkit.launch(headless=False)
    # 修正：直接解構 iphone 參數，不重複傳入 has_touch
    context = browser.new_context(**iphone)
    page = context.new_page()

    console_logs = []
    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: console_logs.append(f"[JS ERROR] {err}"))

    # 1. 載入本地遊戲
    page.goto(f"file://{html_file}")
    page.wait_for_timeout(1000)
    print("✅ 1. 成功載入遊戲畫面")

    # 2. 自動移動至街區終點
    page.evaluate("() => { player.x = 3200; player.hp = 100; }")
    page.keyboard.down("KeyD")
    page.wait_for_timeout(1000)
    page.keyboard.up("KeyD")
    print("✅ 2. 到達夜店門口")

    # 3. 檢查對話框是否彈出並截圖
    page.wait_for_selector("#dialog-box", state="visible", timeout=6000)
    page.screenshot(path="step1_dialog_open.png")
    print("📸 已截圖：step1_dialog_open.png (對話框彈出畫面)")

    # 4. 模擬 iPhone 真實手指點擊選項按鈕
    opt_btn = page.locator(".btn-opt1")
    opt_btn.tap()
    print("👆 已點擊【🌈 好啊，多元成家！】")
    page.wait_for_timeout(800)

    # 5. 擷取進入夜店第一幀畫面
    page.screenshot(path="step2_entered_club.png")
    print("📸 已截圖：step2_entered_club.png (進夜店第一時間畫面)")

    # 6. 模擬手指按住下方的「▶」前進按鍵 2 秒
    right_btn = page.locator("#btn-right")
    right_btn.dispatch_event("pointerdown")
    page.wait_for_timeout(2000)
    right_btn.dispatch_event("pointerup")
    print("👆 已模擬手指長按【▶】按鈕 2 秒")

    # 7. 擷取移動測試後的畫面
    page.screenshot(path="step3_after_moving.png")
    print("📸 已截圖：step3_after_moving.png (按完右鍵後的畫面)")

    # 8. 抓取遊戲底層核心內部變數
    diagnostics = page.evaluate("""() => {
        return {
            currentScene: currentScene,
            isDialogueOpen: isDialogueOpen,
            dialogDisplay: document.getElementById('dialog-box').style.display,
            playerX: player.x,
            playerY: player.y,
            playerVX: player.vx,
            playerVY: player.vy,
            playerGrounded: player.grounded,
            playerH: player.h,
            playerW: player.w,
            cameraX: cameraX,
            keysState: keys,
            totalPlatforms: platforms.length
        };
    }""")

    # 9. 寫入診斷報表
    with open("diagnostic_report.txt", "w", encoding="utf-8") as f:
        f.write("=== 遊戲底層變數狀態診斷 ===\n")
        for k, v in diagnostics.items():
            f.write(f"{k}: {v}\n")
        f.write("\n=== 瀏覽器 Console 日誌紀錄 ===\n")
        f.write("\n".join(console_logs) if console_logs else "無報錯日誌 (正常)")

    browser.close()
    print("========================================")
    print("🎉 巡檢完成！已產出 3 張階段截圖與 diagnostic_report.txt")
    print("========================================")