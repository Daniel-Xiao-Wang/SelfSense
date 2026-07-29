import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

test("renders SelfSense brand", () => {
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>
  );
  expect(screen.getAllByText(/SelfSense/i).length).toBeGreaterThan(0);
});
