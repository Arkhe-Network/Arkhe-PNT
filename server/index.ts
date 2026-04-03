import express from "express";
import cors from "cors";
import { createServer as createViteServer } from "vite";
import path from "path";
import { state } from "./state";
import { runSimulationTick } from "./simulation";
import { setupRoutes } from "./routes";
import { setupPresenceServer } from "./presence_field_server";
import { setupLucentCollector } from "./lucent_omega";
import { logger } from "./logger";
import { startAgentGrpcServer } from "./agent_grpc_server";

// SSE Clients
const clients: express.Response[] = [];

function broadcastState() {
  const data = `data: ${JSON.stringify(state)}\n\n`;
  clients.forEach(client => client.write(data));
}

// Simulation Loop
setInterval(() => {
  runSimulationTick(broadcastState);
}, 1000);

async function startServer() {
  const app = express();
  const PORT = 3000;
  
  // Configure CORS
  app.use(cors({
    origin: process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
  }));

  app.use(express.json());

  // Serve static files for the presence field UI
  app.use("/static", express.static(path.join(process.cwd(), "static")));

  // Setup API Routes
  setupRoutes(app, broadcastState, clients);

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*all', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  const server = app.listen(PORT, "0.0.0.0", () => {
    logger.info(`Server running on http://localhost:${PORT}`);
  });

  // Attach presence server
  setupPresenceServer(server);

  // Initialize Lucent-Ω Collector (qhttp)
  setupLucentCollector();

  // Start Agent gRPC Server
  startAgentGrpcServer();
}

startServer();
