import { Request, Response } from "express";

export default function healthCheck(req: Request, res: Response) {
    return res.status(200).json({ status: "ok", timestamp: new Date().toISOString() });
}