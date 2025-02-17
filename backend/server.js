const fastify = require("fastify")({ logger: true });

fastify.get("/", async (request, reply) => {
  return { status: "✅ StealthTrader Backend Running" };
});

const start = async () => {
  try {
    await fastify.listen({ port: 8000 });
    console.log("🚀 Server running on http://localhost:8000");
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();

