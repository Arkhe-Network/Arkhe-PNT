import * as ecc from 'tiny-secp256k1';
import { ECPairFactory } from 'ecpair';
import * as bitcoin from 'bitcoinjs-lib';
import { logger } from './server/logger.js';

const ECPair = ECPairFactory(ecc);

const keyPair = ECPair.makeRandom();
const { address } = bitcoin.payments.p2pkh({ pubkey: keyPair.publicKey });

logger.info(address || '');
