import { createTRPCReact } from "@trpc/react-query";
import { AppRouter } from "../backend/trpcRouter";

export const trpc = createTRPCReact<AppRouter>();
