import rateLimit, { ipKeyGenerator }  from "express-rate-limit";

const limiter = rateLimit({
	windowMs: 24 * 60 * 60 * 1000,
	limit: 10,
	standardHeaders: 'draft-8',
	legacyHeaders: false,
	keyGenerator: (req) => ipKeyGenerator(req.ip),
})

export default limiter;
