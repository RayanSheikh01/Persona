# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat.spec.ts >> chat flow
- Location: e2e\chat.spec.ts:4:5

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('[data-testid=\'new-chat\']')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - complementary [ref=e3]:
      - generic [ref=e4]:
        - generic [ref=e5]: persona
        - link "memories" [ref=e6] [cursor=pointer]:
          - /url: /memories
          - img [ref=e7]
          - text: memories
      - button "new chat" [ref=e10] [cursor=pointer]:
        - img
        - text: new chat
      - navigation [ref=e11]:
        - list [ref=e12]:
          - listitem [ref=e13]:
            - button "Seed data May 18" [ref=e14] [cursor=pointer]:
              - generic [ref=e15]: Seed data
              - generic [ref=e16]: May 18
          - listitem [ref=e17]:
            - button "hi May 18" [ref=e18] [cursor=pointer]:
              - generic [ref=e19]: hi
              - generic [ref=e20]: May 18
          - listitem [ref=e21]:
            - button "hi May 18" [ref=e22] [cursor=pointer]:
              - generic [ref=e23]: hi
              - generic [ref=e24]: May 18
          - listitem [ref=e25]:
            - button "hi May 18" [ref=e26] [cursor=pointer]:
              - generic [ref=e27]: hi
              - generic [ref=e28]: May 18
          - listitem [ref=e29]:
            - button "untitled May 18" [ref=e30] [cursor=pointer]:
              - generic [ref=e31]: untitled
              - generic [ref=e32]: May 18
          - listitem [ref=e33]:
            - button "untitled May 18" [ref=e34] [cursor=pointer]:
              - generic [ref=e35]: untitled
              - generic [ref=e36]: May 18
          - listitem [ref=e37]:
            - button "untitled May 18" [ref=e38] [cursor=pointer]:
              - generic [ref=e39]: untitled
              - generic [ref=e40]: May 18
          - listitem [ref=e41]:
            - button "untitled May 18" [ref=e42] [cursor=pointer]:
              - generic [ref=e43]: untitled
              - generic [ref=e44]: May 18
          - listitem [ref=e45]:
            - button "untitled May 18" [ref=e46] [cursor=pointer]:
              - generic [ref=e47]: untitled
              - generic [ref=e48]: May 18
          - listitem [ref=e49]:
            - button "untitled May 18" [ref=e50] [cursor=pointer]:
              - generic [ref=e51]: untitled
              - generic [ref=e52]: May 18
          - listitem [ref=e53]:
            - button "untitled May 18" [ref=e54] [cursor=pointer]:
              - generic [ref=e55]: untitled
              - generic [ref=e56]: May 18
          - listitem [ref=e57]:
            - button "untitled May 18" [ref=e58] [cursor=pointer]:
              - generic [ref=e59]: untitled
              - generic [ref=e60]: May 18
          - listitem [ref=e61]:
            - button "untitled May 18" [ref=e62] [cursor=pointer]:
              - generic [ref=e63]: untitled
              - generic [ref=e64]: May 18
          - listitem [ref=e65]:
            - button "untitled May 18" [ref=e66] [cursor=pointer]:
              - generic [ref=e67]: untitled
              - generic [ref=e68]: May 18
          - listitem [ref=e69]:
            - button "untitled May 18" [ref=e70] [cursor=pointer]:
              - generic [ref=e71]: untitled
              - generic [ref=e72]: May 18
          - listitem [ref=e73]:
            - button "untitled May 18" [ref=e74] [cursor=pointer]:
              - generic [ref=e75]: untitled
              - generic [ref=e76]: May 18
          - listitem [ref=e77]:
            - button "untitled May 18" [ref=e78] [cursor=pointer]:
              - generic [ref=e79]: untitled
              - generic [ref=e80]: May 18
          - listitem [ref=e81]:
            - button "untitled May 18" [ref=e82] [cursor=pointer]:
              - generic [ref=e83]: untitled
              - generic [ref=e84]: May 18
          - listitem [ref=e85]:
            - button "untitled May 18" [ref=e86] [cursor=pointer]:
              - generic [ref=e87]: untitled
              - generic [ref=e88]: May 18
    - generic [ref=e89]:
      - paragraph [ref=e92]: start a new conversation
      - generic [ref=e94]:
        - textbox "message persona…" [ref=e95]
        - button [disabled]:
          - img
    - complementary [ref=e96]:
      - heading "memories used" [level=2] [ref=e98]
      - paragraph [ref=e100]: none yet — memories surfaced for the current turn appear here
  - alert [ref=e101]
```

# Test source

```ts
  1  | 
  2  | import { test, expect } from "@playwright/test";
  3  | 
  4  | test("chat flow", async ({ page }) => {
  5  |   await page.goto("/");
> 6  |   await page.click("[data-testid='new-chat']");
     |              ^ Error: page.click: Test timeout of 30000ms exceeded.
  7  |     await page.fill("textarea[placeholder='message persona…']", "Hello, who are you?");
  8  |     await page.click("button:has-text('Send')");
  9  |     await expect(page.locator("text=Hello, who are you?")).toBeVisible();
  10 |     await expect(page.locator("text=memories used")).toBeVisible({ timeout: 30000 });
  11 | });
  12 | 
  13 | 
  14 | test("visit memories and click goal chip", async ({ page }) => {
  15 |     await page.goto("/memories");
  16 |     await page.click("text=goals");
  17 |     // assert that the goal details are visible
  18 |     await expect(page.locator("text=goal details")).toBeVisible();
  19 | });
  20 | 
```