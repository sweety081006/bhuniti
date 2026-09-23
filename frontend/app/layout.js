import "./globals.css";

import Shell from "../components/Shell";

export const metadata = {
  title: "BhuNiti — Land Governance Research & Policy Platform",
  description:
    "National Digital Platform for Research, Policy Innovation and Evidence-Based Land Governance.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
