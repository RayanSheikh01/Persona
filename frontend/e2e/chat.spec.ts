import { test, expect } from "@playwright/test";

test("new chat: send a message and see assistant response with memory rail", async ({
  page,
}) => {
  await page.goto("/");

  await page.getByRole("button", { name: /new chat/i }).click();

  const input = page.getByPlaceholder("message persona…");
  await input.fill("Hello, who are you?");
  await input.press("Enter");

  await expect(page.getByText("Hello, who are you?")).toBeVisible();

  await expect(
    page.getByRole("heading", { name: /memories used/i }),
  ).toBeVisible();

  // assistant response appears (slack: HF Inference can be slow on cold start)
  await expect
    .poll(
      async () =>
        await page.locator("div.bg-zinc-900.text-zinc-100").count(),
      { timeout: 30_000 },
    )
    .toBeGreaterThan(0);
});

test("memories page: filter by goal chip", async ({ page }) => {
  await page.goto("/memories");

  const goalChip = page.getByRole("button", { name: /^goal$/i });
  await expect(goalChip).toBeVisible();
  await goalChip.click();

  await expect(goalChip).toHaveClass(/bg-zinc-100/);
});
