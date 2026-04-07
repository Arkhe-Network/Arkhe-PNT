import express from 'express';
import passport from 'passport';
import { Strategy as JwtStrategy, ExtractJwt } from 'passport-jwt';
import jwt from 'jsonwebtoken';
import { Sequelize, DataTypes } from 'sequelize';
import { logger } from '@arkhe/shared';

const app = express();
app.use(express.json());

const JWT_SECRET = process.env.JWT_SECRET || 'arkhe_secret_999';

// --- DATABASE (SEQUELIZE) ---
const sequelize = new Sequelize(process.env.DATABASE_URL || 'sqlite::memory:');

const User = sequelize.define('User', {
  username: { type: DataTypes.STRING, unique: true },
  password: { type: DataTypes.STRING },
});

// --- AUTHENTICATION (PASSPORT/JWT) ---
const opts = {
  jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
  secretOrKey: JWT_SECRET,
};

passport.use(
  new JwtStrategy(opts, async (jwt_payload, done) => {
    try {
      const user = await User.findByPk(jwt_payload.sub);
      if (user) return done(null, user);
      return done(null, false);
    } catch (err) {
      return done(err, false);
    }
  })
);

app.post('/login', async (req, res) => {
  const { username } = req.body;
  // Simplified login for the ecosystem demo
  const token = jwt.sign({ sub: username }, JWT_SECRET, { expiresIn: '1h' });
  res.json({ access_token: token });
});

app.get('/protected', passport.authenticate('jwt', { session: false }), (req, res) => {
  res.json({ message: 'Secure access to Arkhe-Chain Bridge granted.', user: req.user });
});

const start = async () => {
  try {
    await sequelize.sync();
    app.listen(3001, () => {
      logger.info('Express Bridge Service running on port 3001');
    });
  } catch (err) {
    logger.error(err);
  }
};

start();
