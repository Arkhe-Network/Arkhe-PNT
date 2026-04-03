from playwright.sync_api import sync_playwright, expect
import time

def verify_enterprise_plus(page):
    # 1. Acessar o CommandCenter
    page.goto("http://localhost:3000")
    page.wait_for_load_state("networkidle")
    time.sleep(2) # Wait for React to mount

    # 2. Navegar para a aba Wetware
    wetware_tab = page.get_by_role("button", name="Wetware")
    expect(wetware_tab).to_be_visible()
    wetware_tab.click()

    # 3. Abrir o painel Enterprise Plus
    enterprise_button = page.get_by_role("button", name="Arkhe(n) Enterprise Plus (25 Agents)")
    expect(enterprise_button).to_be_visible()
    enterprise_button.click()

    # 4. Acionar o subagente G1 (Nomos)
    g1_button = page.get_by_role("button", name="ACIONAR Nomos POC")
    expect(g1_button).to_be_visible()
    g1_button.click()

    # 5. Verificar o status verificado (ZK-PROOF)
    # O backend retorna um log com [ZK-PROOF: VERIFICADO]
    status_text = page.get_by_text("[ZK-PROOF: VERIFICADO]")
    expect(status_text).to_be_visible()

    # 6. Tirar screenshot
    page.screenshot(path="/app/verification/poc_verified_final.png", full_page=True)
    print("Screenshot salva em /app/verification/poc_verified_final.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = context.new_page()
        try:
            verify_enterprise_plus(page)
        except Exception as e:
            print(f"Erro na verificação: {e}")
            page.screenshot(path="/app/verification/error.png")
        finally:
            browser.close()
