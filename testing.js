const crypto = require('crypto');
const EC = require('elliptic').ec;

// Initialize elliptic curve (SECP256k1 is commonly used in Bitcoin)
const ec = new EC('secp256k1');

// Generate ECDH key pair
function generateECDHKeyPair(textSeed) {
    // Convert the text seed to bytes
    const textSeedBytes = Buffer.from(textSeed, 'utf-8');

    // Generate SHA-256 hash of the text seed
    const hashBytes = crypto.createHash('sha256').update(textSeedBytes).digest();

    // Use the hash output as a seed for a deterministic elliptic curve key pair generation
    const keyPair = ec.keyFromPrivate(hashBytes);
    return {
        privateKey: keyPair.getPrivate(),
        publicKey: keyPair.getPublic()
    };
}

// Derive shared secret given your private key and other party's public key
function deriveSharedSecret(privateKey, otherPublicKey) {
    const keyPair = ec.keyFromPrivate(privateKey);
    const sharedSecret = keyPair.derive(otherPublicKey);
    return sharedSecret.toString('hex');
}

// Encryption function using AES
function encrypt(text, sharedSecret) {
    const cipher = crypto.createCipher('aes-256-cbc', sharedSecret);
    let encrypted = cipher.update(text, 'utf-8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
}

// Decryption function using AES
function decrypt(encrypted, sharedSecret) {
    const decipher = crypto.createDecipher('aes-256-cbc', sharedSecret);
    let decrypted = decipher.update(encrypted, 'hex', 'utf-8');
    decrypted += decipher.final('utf-8');
    return decrypted;
}

// Example usage
const textSeed = "my secret text seed";

// Alice's side
const aliceKeyPair = generateECDHKeyPair(textSeed);

// Bob's side
const bobKeyPair = generateECDHKeyPair(textSeed);

// Derive shared secrets
const aliceSharedSecret = deriveSharedSecret(aliceKeyPair.privateKey, bobKeyPair.publicKey);
const bobSharedSecret = deriveSharedSecret(bobKeyPair.privateKey, aliceKeyPair.publicKey);

console.log('Alice shared secret:', aliceSharedSecret);
console.log('Bob shared secret:', bobSharedSecret);

// Encrypt message from Alice to Bob
const messageFromAlice = "Hello Bob!";
const encryptedMessage = encrypt(messageFromAlice, aliceSharedSecret);
console.log('Encrypted message from Alice to Bob:', encryptedMessage);

// Decrypt message from Alice by Bob
const decryptedMessage = decrypt(encryptedMessage, bobSharedSecret);
console.log('Decrypted message by Bob:', decryptedMessage);

console.log(aliceKeyPair.privateKey.constructor.name); // This will output "BN"
