import path from "node:path";
import express, { Request, Response } from "express";

const app = express();
const port = Number(process.env.PORT) || 3000;
const host = process.env.HOST || "0.0.0.0";

app.use(express.static(path.join(__dirname, "..", "public")));

app.get("/api/health", (_request: Request, response: Response) => {
  response.json({ status: "ok" });
});

app.listen(port, host, () => {
  console.log(`Website is running at http://127.0.0.1:${port}`);
  console.log(`Network access is available at http://<your-ip>:${port}`);
});
