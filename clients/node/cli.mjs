#!/usr/bin/env node

import { fetch } from 'undici';
import WebSocket from 'ws';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

const getRelationship = async (name, url = 'http://localhost:8000', apiKey = 'dev', stream = false) => {
  if (!stream) {
    // HTTP request
    try {
      const response = await fetch(`${url}/relationship?name=${encodeURIComponent(name)}`, {
        headers: { 'X-API-Key': apiKey }
      });
      const data = await response.json();
      console.log(JSON.stringify(data, null, 2));
    } catch (err) {
      console.error('Error:', err.message);
    }
    return;
  }

  // WebSocket streaming
  const ws = new WebSocket(`${url.replace('http', 'ws')}/relationship/stream`, {
    headers: { 'X-API-Key': apiKey }
  });

  ws.on('open', () => {
    ws.send(JSON.stringify({ name, trace: true }));
  });

  ws.on('message', (data) => {
    console.log(JSON.stringify(JSON.parse(data.toString()), null, 2));
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error.message);
  });

  ws.on('close', () => {
    process.exit(0);
  });
};

// Parse command line arguments
const argv = yargs(hideBin(process.argv))
  .option('name', {
    alias: 'n',
    type: 'string',
    description: 'Name to look up',
    demandOption: true
  })
  .option('url', {
    alias: 'u',
    type: 'string',
    description: 'Service URL',
    default: 'http://localhost:8000'
  })
  .option('api-key', {
    alias: 'k',
    type: 'string',
    description: 'API key',
    default: 'dev'
  })
  .option('stream', {
    alias: 's',
    type: 'boolean',
    description: 'Stream results via WebSocket',
    default: false
  })
  .help()
  .alias('help', 'h')
  .argv;

getRelationship(argv.name, argv.url, argv['api-key'], argv.stream);