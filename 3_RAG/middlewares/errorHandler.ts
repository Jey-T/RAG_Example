import { NextFunction, Request, Response } from 'express';
import { AppError } from '../types/error';

export const errorHandler = async (
    err: Error,
    _: Request,
    res: Response,
    _2: NextFunction
) => {
    let statusCode = 500;
    let message = 'Internal Server Error';

    if (err instanceof AppError) {
        statusCode = err.statusCode;
        message = err.message;
    }

    res.status(statusCode).json({
        message
    });
};