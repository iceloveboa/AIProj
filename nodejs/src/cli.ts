#!/usr/bin/env node

import readline from "node:readline";

type Command = (args: string[]) => void;

let activeTimer: ReturnType<typeof setInterval> | null = null;

const commands: Record<string, Command> = {
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
} else {
  runCommand(command, args);
}

function startPrompt(): void {
  printHelp();

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: "cmd> ",
  });

  rl.prompt();

  rl.on("line", (line: string) => {
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

function runCommand(nextCommand: string, args: string[]): void {
  if (!commands[nextCommand]) {
    console.error(`Unknown command: ${nextCommand}`);
    printHelp();
    process.exitCode = 1;
    return;
  }

  commands[nextCommand](args);
}

function greet(args: string[]): void {
  const name = args[0] || "World";
  console.log(`Hello, ${name}!`);
}

function sum(args: string[]): void {
  const numbers = parseNumbers(args, "sum");

  if (!numbers) {
    return;
  }

  const total = numbers.reduce((result, number) => result + number, 0);
  console.log(total);
}

function mult(args: string[]): void {
  const numbers = parseNumbers(args, "mult");

  if (!numbers) {
    return;
  }

  const result = numbers.reduce((total, number) => total * number, 1);
  console.log(result);
}

function printTime(): void {
  const renderTime = () => {
    readline.clearLine(process.stdout, 0);
    readline.cursorTo(process.stdout, 0);
    process.stdout.write(formatTime(new Date()));
  };

  startActiveTimer(renderTime, 1000);
}

function loading(args: string[]): void {
  const message = args.join(" ") || "Loading";
  const frames = ["|", "/", "-", "\\"];
  let index = 0;

  const renderLoading = () => {
    readline.clearLine(process.stdout, 0);
    readline.cursorTo(process.stdout, 0);
    process.stdout.write(`${frames[index]} ${message}`);
    index = (index + 1) % frames.length;
  };

  startActiveTimer(renderLoading, 120);
}

function startActiveTimer(render: () => void, intervalMs: number): void {
  stopActiveTimer();
  render();
  activeTimer = setInterval(render, intervalMs);
}

function stopActiveTimer(): void {
  if (!activeTimer) {
    return;
  }

  clearInterval(activeTimer);
  activeTimer = null;
}

function formatTime(date: Date): string {
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");

  return `${hours}:${minutes}:${seconds}`;
}

function parseNumbers(args: string[], commandName: "sum" | "mult"): number[] | null {
  const numbers = args.map(Number);

  if (!numbers.length || numbers.some(Number.isNaN)) {
    console.error(`Usage: cli ${commandName} <number...>`);
    process.exitCode = 1;
    return null;
  }

  return numbers;
}

function printHelp(): void {
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

function exit(): void {
  process.exit(0);
}
