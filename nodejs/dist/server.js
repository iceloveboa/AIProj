"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_path_1 = __importDefault(require("node:path"));
const express_1 = __importDefault(require("express"));
const app = (0, express_1.default)();
const port = Number(process.env.PORT) || 3000;
const host = process.env.HOST || "0.0.0.0";
app.use(express_1.default.static(node_path_1.default.join(__dirname, "..", "public")));
app.get("/api/health", (_request, response) => {
    response.json({ status: "ok" });
});
app.listen(port, host, () => {
    console.log(`Website is running at http://127.0.0.1:${port}`);
    console.log(`Network access is available at http://<your-ip>:${port}`);
});
