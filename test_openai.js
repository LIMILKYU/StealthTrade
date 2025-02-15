import dotenv from "dotenv";
import OpenAI from "openai";

dotenv.config();

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY, // .env에서 API 키 가져오기
});

async function runChatGPT() {
    const completion = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [{ role: "system", content: "Hello, how can I assist you?" }],
    });

    console.log(completion.choices[0].message.content);
}

runChatGPT();
