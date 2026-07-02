#!/usr/bin/env node
"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_readline_1 = __importDefault(require("node:readline"));
let activeTimer = null;
const commands = {
    greet,
    sum,
    mult,
    printTime,
    loading,
    exit,
    quit: exit,
    help: printHelp,
};
const [, , command, ...args] = process.argv;
if (!command) {
    startPrompt();
}
else {
    runCommand(command, args);
}
function startPrompt() {
    printHelp();
    const rl = node_readline_1.default.createInterface({
        input: process.stdin,
        output: process.stdout,
        prompt: "cmd> ",
    });
    rl.prompt();
    rl.on("line", (line) => {
        const input = line.trim();
        if (input) {
            const [nextCommand, ...nextArgs] = input.split(/\s+/);
            runCommand(nextCommand, nextArgs);
        }
        rl.prompt();
    });
    rl.on("close", () => {
        stopActiveTimer();
        process.stdout.write("\n");
        console.log("Bye.");
    });
}
function runCommand(nextCommand, args) {
    if (!commands[nextCommand]) {
        console.error(`Unknown command: ${nextCommand}`);
        printHelp();
        process.exitCode = 1;
        return;
    }
    commands[nextCommand](args);
}
function greet(args) {
    const name = args[0] || "World";
    console.log(`Hello, ${name}!`);
}
function sum(args) {
    const numbers = parseNumbers(args, "sum");
    if (!numbers) {
        return;
    }
    const total = numbers.reduce((result, number) => result + number, 0);
    console.log(total);
}
function mult(args) {
    const numbers = parseNumbers(args, "mult");
    if (!numbers) {
        return;
    }
    const result = numbers.reduce((total, number) => total * number, 1);
    console.log(result);
}
function printTime() {
    const renderTime = () => {
        node_readline_1.default.clearLine(process.stdout, 0);
        node_readline_1.default.cursorTo(process.stdout, 0);
        process.stdout.write(formatTime(new Date()));
    };
    startActiveTimer(renderTime, 1000);
}
function loading(args) {
    const message = args.join(" ") || "Loading";
    const frames = ["|", "/", "-", "\\"];
    let index = 0;
    const renderLoading = () => {
        node_readline_1.default.clearLine(process.stdout, 0);
        node_readline_1.default.cursorTo(process.stdout, 0);
        process.stdout.write(`${frames[index]} ${message}`);
        index = (index + 1) % frames.length;
    };
    startActiveTimer(renderLoading, 120);
}
function startActiveTimer(render, intervalMs) {
    stopActiveTimer();
    render();
    activeTimer = setInterval(render, intervalMs);
}
function stopActiveTimer() {
    if (!activeTimer) {
        return;
    }
    clearInterval(activeTimer);
    activeTimer = null;
}
function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
    return `${hours}:${minutes}:${seconds}`;
}
function parseNumbers(args, commandName) {
    const numbers = args.map(Number);
    if (!numbers.length || numbers.some(Number.isNaN)) {
        console.error(`Usage: cli ${commandName} <number...>`);
        process.exitCode = 1;
        return null;
    }
    return numbers;
}
function printHelp() {
    console.log(`Usage:
  cli
  cli help
  cli greet [name]
  cli sum <number...>
  cli mult <number...>
  cli printTime
  cli loading [message]

Interactive commands:
  help
  greet [name]
  sum <number...>
  mult <number...>
  printTime
  loading [message]
  exit
`);
}
function exit() {
    process.exit(0);
}
