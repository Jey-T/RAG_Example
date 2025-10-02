import rateLimit from "express-rate-limit";


const limiter = rateLimit({
	windowMs: 24 * 60 * 60 * 1000, 
	limit: 3, 
	standardHeaders: 'draft-8',
	legacyHeaders: false,
	ipv6Subnet: 56,
})

export default limiter;
