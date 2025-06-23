import type { Meta, StoryObj } from "@storybook/react";
import {
  expect,
  fn,
  screen,
  userEvent,
  waitFor,
  within,
} from "@storybook/test";

import { ZaaktypeFilter as ZaaktypeFilterComponent } from "./ZaaktypeFilter";

const meta: Meta<typeof ZaaktypeFilterComponent> = {
  title: "Components/ZaaktypeFilter",
  component: ZaaktypeFilterComponent,
};

export default meta;
type Story = StoryObj<typeof meta>;

export const ZaaktypeFilter: Story = {
  args: {
    children: "The quick brown fox jumps over the lazy dog.",
    onSubmit: fn(),
  },
  play: async ({ args, canvasElement }) => {
    const trefwoorden = await within(canvasElement).findByRole("textbox", {
      name: "Trefwoorden",
    });
    await userEvent.type(trefwoorden, "foo");
    await expect(trefwoorden).toHaveValue("foo");

    const dropdown = await within(canvasElement).findByText("Filter");
    await userEvent.click(dropdown);

    const radios = await screen.findAllByRole("radio");
    for (const option of radios) {
      await userEvent.click(option);
      await expect(option).toBeChecked();
    }

    const submit = await screen.findByRole("button", { name: "Pas toe" });
    await userEvent.click(submit);
    await waitFor(() => expect(args.onSubmit).toHaveBeenCalled());

    const reset = await screen.findByRole("button", {
      name: "Wis alle filters",
    });

    await userEvent.click(reset);
    await expect(trefwoorden).toHaveValue("");
    for (const option of radios) {
      await expect(option).not.toBeChecked();
    }

    const annuleer = await screen.findByRole("button", { name: "Annuleer" });
    await userEvent.click(annuleer);
    expect(annuleer).not.toBeVisible();

    await userEvent.click(dropdown);
  },
};
